import json
from io import StringIO

import pandas as pd
import streamlit as st

from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Local AI Operations Copilot",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# LOAD LOCAL LANGUAGE MODEL
# --------------------------------------------------

@st.cache_resource
def load_language_model():
    """
    Load and cache Mistral through the LangChain
    Ollama integration.
    """

    return ChatOllama(
        model="mistral",
        temperature=0
    )


# --------------------------------------------------
# VALIDATE CSV DATA
# --------------------------------------------------

def validate_dataframe(dataframe):
    """
    Validate the structure and contents of the uploaded CSV.
    """

    required_columns = [
        "Month",
        "JobsRaised",
        "JobsCompleted",
        "JobsCancelled"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        return (
            False,
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    numeric_columns = [
        "JobsRaised",
        "JobsCompleted",
        "JobsCancelled"
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

    if dataframe[numeric_columns].isna().any().any():
        return (
            False,
            "The KPI columns contain missing or "
            "non-numeric values."
        )

    if (dataframe[numeric_columns] < 0).any().any():
        return (
            False,
            "KPI values cannot be negative."
        )

    if (dataframe["JobsRaised"] == 0).any():
        return (
            False,
            "JobsRaised cannot be zero because KPI rates "
            "must be calculated."
        )

    impossible_rows = dataframe[
        (
            dataframe["JobsCompleted"]
            + dataframe["JobsCancelled"]
        )
        > dataframe["JobsRaised"]
    ]

    if not impossible_rows.empty:
        return (
            False,
            "Some rows have JobsCompleted plus JobsCancelled "
            "greater than JobsRaised."
        )

    return True, "Data validation passed."


# --------------------------------------------------
# TOOL 1: KPI SUMMARY
# --------------------------------------------------

@tool
def calculate_kpi_summary(csv_text: str) -> str:
    """
    Calculate overall operational KPI totals and rates.

    Use this tool for questions about general KPI totals,
    completion rates, cancellation rates and unresolved work.
    """

    dataframe = pd.read_csv(
        StringIO(csv_text)
    )

    total_raised = int(
        dataframe["JobsRaised"].sum()
    )

    total_completed = int(
        dataframe["JobsCompleted"].sum()
    )

    total_cancelled = int(
        dataframe["JobsCancelled"].sum()
    )

    total_unresolved = (
        total_raised
        - total_completed
        - total_cancelled
    )

    completion_rate = (
        total_completed
        / total_raised
        * 100
    )

    cancellation_rate = (
        total_cancelled
        / total_raised
        * 100
    )

    unresolved_rate = (
        total_unresolved
        / total_raised
        * 100
    )

    result = {
        "tool_used": "kpi_summary",
        "total_jobs_raised": total_raised,
        "total_jobs_completed": total_completed,
        "total_jobs_cancelled": total_cancelled,
        "total_unresolved_jobs": int(
            total_unresolved
        ),
        "overall_completion_rate": round(
            completion_rate,
            2
        ),
        "overall_cancellation_rate": round(
            cancellation_rate,
            2
        ),
        "overall_unresolved_rate": round(
            unresolved_rate,
            2
        )
    }

    return json.dumps(
        result,
        indent=2
    )


# --------------------------------------------------
# TOOL 2: MONTHLY TREND ANALYSIS
# --------------------------------------------------

@tool
def analyse_monthly_trends(csv_text: str) -> str:
    """
    Analyse changes between the first and final periods.

    Use this tool for questions about trends, changes
    over time and first-period versus final-period results.
    """

    dataframe = pd.read_csv(
        StringIO(csv_text)
    )

    dataframe["CompletionRate"] = (
        dataframe["JobsCompleted"]
        / dataframe["JobsRaised"]
        * 100
    )

    dataframe["CancellationRate"] = (
        dataframe["JobsCancelled"]
        / dataframe["JobsRaised"]
        * 100
    )

    dataframe["UnresolvedJobs"] = (
        dataframe["JobsRaised"]
        - dataframe["JobsCompleted"]
        - dataframe["JobsCancelled"]
    )

    first_row = dataframe.iloc[0]
    last_row = dataframe.iloc[-1]

    result = {
        "tool_used": "monthly_trend",
        "first_month": str(
            first_row["Month"]
        ),
        "last_month": str(
            last_row["Month"]
        ),
        "first_month_jobs_raised": int(
            first_row["JobsRaised"]
        ),
        "last_month_jobs_raised": int(
            last_row["JobsRaised"]
        ),
        "jobs_raised_change": int(
            last_row["JobsRaised"]
            - first_row["JobsRaised"]
        ),
        "first_month_jobs_completed": int(
            first_row["JobsCompleted"]
        ),
        "last_month_jobs_completed": int(
            last_row["JobsCompleted"]
        ),
        "jobs_completed_change": int(
            last_row["JobsCompleted"]
            - first_row["JobsCompleted"]
        ),
        "first_month_jobs_cancelled": int(
            first_row["JobsCancelled"]
        ),
        "last_month_jobs_cancelled": int(
            last_row["JobsCancelled"]
        ),
        "jobs_cancelled_change": int(
            last_row["JobsCancelled"]
            - first_row["JobsCancelled"]
        ),
        "first_month_completion_rate": round(
            float(first_row["CompletionRate"]),
            2
        ),
        "last_month_completion_rate": round(
            float(last_row["CompletionRate"]),
            2
        ),
        "completion_rate_change_points": round(
            float(
                last_row["CompletionRate"]
                - first_row["CompletionRate"]
            ),
            2
        ),
        "first_month_cancellation_rate": round(
            float(first_row["CancellationRate"]),
            2
        ),
        "last_month_cancellation_rate": round(
            float(last_row["CancellationRate"]),
            2
        ),
        "cancellation_rate_change_points": round(
            float(
                last_row["CancellationRate"]
                - first_row["CancellationRate"]
            ),
            2
        ),
        "first_month_unresolved_jobs": int(
            first_row["UnresolvedJobs"]
        ),
        "last_month_unresolved_jobs": int(
            last_row["UnresolvedJobs"]
        )
    }

    return json.dumps(
        result,
        indent=2
    )


# --------------------------------------------------
# TOOL 3: CANCELLATION ANALYSIS
# --------------------------------------------------

@tool
def analyse_cancellations(csv_text: str) -> str:
    """
    Analyse cancellation volumes and rates.

    Use this tool for questions about cancellations,
    cancellation growth and the highest cancellation period.
    """

    dataframe = pd.read_csv(
        StringIO(csv_text)
    )

    dataframe["CancellationRate"] = (
        dataframe["JobsCancelled"]
        / dataframe["JobsRaised"]
        * 100
    )

    highest_volume_index = (
        dataframe["JobsCancelled"].idxmax()
    )

    highest_rate_index = (
        dataframe["CancellationRate"].idxmax()
    )

    first_row = dataframe.iloc[0]
    last_row = dataframe.iloc[-1]

    highest_volume_row = dataframe.loc[
        highest_volume_index
    ]

    highest_rate_row = dataframe.loc[
        highest_rate_index
    ]

    cancellation_count_change = int(
        last_row["JobsCancelled"]
        - first_row["JobsCancelled"]
    )

    if int(first_row["JobsCancelled"]) > 0:
        cancellation_percentage_change = (
            cancellation_count_change
            / int(first_row["JobsCancelled"])
            * 100
        )

        cancellation_percentage_change = round(
            cancellation_percentage_change,
            2
        )

    else:
        cancellation_percentage_change = (
            "Not available"
        )

    result = {
        "tool_used": "cancellation_analysis",
        "highest_cancellation_volume_month": str(
            highest_volume_row["Month"]
        ),
        "highest_cancellation_count": int(
            highest_volume_row["JobsCancelled"]
        ),
        "highest_cancellation_rate_month": str(
            highest_rate_row["Month"]
        ),
        "highest_cancellation_rate": round(
            float(
                highest_rate_row["CancellationRate"]
            ),
            2
        ),
        "first_month": str(
            first_row["Month"]
        ),
        "first_month_cancellations": int(
            first_row["JobsCancelled"]
        ),
        "first_month_cancellation_rate": round(
            float(first_row["CancellationRate"]),
            2
        ),
        "last_month": str(
            last_row["Month"]
        ),
        "last_month_cancellations": int(
            last_row["JobsCancelled"]
        ),
        "last_month_cancellation_rate": round(
            float(last_row["CancellationRate"]),
            2
        ),
        "cancellation_count_change": (
            cancellation_count_change
        ),
        "cancellation_percentage_change": (
            cancellation_percentage_change
        )
    }

    return json.dumps(
        result,
        indent=2
    )


# --------------------------------------------------
# TOOL 4: COMPLETION ANALYSIS
# --------------------------------------------------

@tool
def analyse_completions(csv_text: str) -> str:
    """
    Analyse completion volumes and completion rates.

    Use this tool for questions about completed jobs,
    delivery performance and completion-rate changes.
    """

    dataframe = pd.read_csv(
        StringIO(csv_text)
    )

    dataframe["CompletionRate"] = (
        dataframe["JobsCompleted"]
        / dataframe["JobsRaised"]
        * 100
    )

    highest_volume_index = (
        dataframe["JobsCompleted"].idxmax()
    )

    highest_rate_index = (
        dataframe["CompletionRate"].idxmax()
    )

    lowest_rate_index = (
        dataframe["CompletionRate"].idxmin()
    )

    first_row = dataframe.iloc[0]
    last_row = dataframe.iloc[-1]

    result = {
        "tool_used": "completion_analysis",
        "highest_completion_volume_month": str(
            dataframe.loc[
                highest_volume_index,
                "Month"
            ]
        ),
        "highest_completion_volume": int(
            dataframe.loc[
                highest_volume_index,
                "JobsCompleted"
            ]
        ),
        "highest_completion_rate_month": str(
            dataframe.loc[
                highest_rate_index,
                "Month"
            ]
        ),
        "highest_completion_rate": round(
            float(
                dataframe.loc[
                    highest_rate_index,
                    "CompletionRate"
                ]
            ),
            2
        ),
        "lowest_completion_rate_month": str(
            dataframe.loc[
                lowest_rate_index,
                "Month"
            ]
        ),
        "lowest_completion_rate": round(
            float(
                dataframe.loc[
                    lowest_rate_index,
                    "CompletionRate"
                ]
            ),
            2
        ),
        "first_month_completion_rate": round(
            float(first_row["CompletionRate"]),
            2
        ),
        "last_month_completion_rate": round(
            float(last_row["CompletionRate"]),
            2
        ),
        "completion_rate_change_points": round(
            float(
                last_row["CompletionRate"]
                - first_row["CompletionRate"]
            ),
            2
        )
    }

    return json.dumps(
        result,
        indent=2
    )


# --------------------------------------------------
# TOOL ROUTER
# --------------------------------------------------

def select_tool(
    question,
    language_model
):
    """
    Ask Mistral to select one analytical tool for
    the user's business question.
    """

    routing_prompt = f"""
You are the routing component of an operations analytics agent.

Select exactly one analytical tool for the user's question.

AVAILABLE TOOLS:

1. kpi_summary
Use for total jobs, overall rates, unresolved work and
general KPI summaries.

2. monthly_trend
Use for changes over time, period comparisons, growth,
and increasing or decreasing operational performance.

3. cancellation_analysis
Use specifically for cancelled jobs, cancellation growth,
cancellation rates and the highest cancellation period.

4. completion_analysis
Use specifically for completed jobs, completion rates
and delivery performance.

USER QUESTION:

{question}

Return only one exact value:

kpi_summary
monthly_trend
cancellation_analysis
completion_analysis
"""

    response = language_model.invoke(
        routing_prompt
    )

    model_selection = (
        response.content
        .strip()
        .lower()
    )

    tool_names = [
        "kpi_summary",
        "monthly_trend",
        "cancellation_analysis",
        "completion_analysis"
    ]

    for tool_name in tool_names:
        if tool_name in model_selection:
            return tool_name

    return "kpi_summary"


# --------------------------------------------------
# EXECUTE SELECTED TOOL
# --------------------------------------------------

def execute_selected_tool(
    selected_tool,
    csv_text
):
    """
    Execute the analytical tool selected by the AI router.
    """

    tool_input = {
        "csv_text": csv_text
    }

    if selected_tool == "monthly_trend":
        return analyse_monthly_trends.invoke(
            tool_input
        )

    if selected_tool == "cancellation_analysis":
        return analyse_cancellations.invoke(
            tool_input
        )

    if selected_tool == "completion_analysis":
        return analyse_completions.invoke(
            tool_input
        )

    return calculate_kpi_summary.invoke(
        tool_input
    )


# --------------------------------------------------
# GENERATE MANAGEMENT RESPONSE
# --------------------------------------------------

def generate_management_response(
    question,
    selected_tool,
    verified_result,
    language_model
):
    """
    Convert verified Python calculations into a
    professional management explanation.
    """

    response_prompt = f"""
You are an operations data analyst.

Answer the user's question using only the verified
analytical result supplied below.

USER QUESTION:

{question}

SELECTED ANALYTICAL TOOL:

{selected_tool}

VERIFIED PYTHON RESULT:

{verified_result}

RULES:

1. Use only the verified result.
2. Do not invent causes or unsupported facts.
3. Separate confirmed facts from hypotheses.
4. Label unproven explanations as areas for investigation.
5. Provide practical and proportionate management actions.
6. Do not claim that correlation proves causation.
7. Use UK English.
8. Keep the response clear and professional.

Use these headings:

Verified Findings

Areas for Investigation

Recommended Actions
"""

    response = language_model.invoke(
        response_prompt
    )

    return response.content


# --------------------------------------------------
# GENERATE STAKEHOLDER EMAIL
# --------------------------------------------------

def generate_stakeholder_email(
    question,
    selected_tool,
    verified_result,
    management_response,
    language_model
):
    """
    Create a professional stakeholder email based only
    on verified calculations and the management analysis.
    """

    email_prompt = f"""
You are an operations analyst preparing a stakeholder email.

Create a concise professional email using only the
information supplied below.

BUSINESS QUESTION:

{question}

SELECTED ANALYTICAL TOOL:

{selected_tool}

VERIFIED PYTHON RESULT:

{verified_result}

MANAGEMENT ANALYSIS:

{management_response}

RULES:

1. Use only the supplied information.
2. Do not invent causes, explanations or statistics.
3. Separate verified facts from areas requiring investigation.
4. Use UK English.
5. Use a professional and concise tone.
6. Include a clear subject line.
7. Include a short summary of verified findings.
8. Include practical next steps.
9. Do not include a recipient name.
10. Do not include unsupported claims.
11. Do not mention the AI model or prompt.

Use this exact structure:

Subject:

Hello,

Summary:

Recommended next steps:

Kind regards,
Operations Analytics Team
"""

    response = language_model.invoke(
        email_prompt
    )

    return response.content


# --------------------------------------------------
# CREATE DOWNLOADABLE REPORT
# --------------------------------------------------

def create_management_report(
    question,
    selected_tool,
    verified_result,
    management_response
):
    """
    Create a downloadable management report.
    """

    report_lines = [
        "LOCAL AI OPERATIONS COPILOT",
        "=" * 50,
        "",
        "BUSINESS QUESTION",
        "-" * 25,
        question,
        "",
        "SELECTED TOOL",
        "-" * 25,
        selected_tool,
        "",
        "VERIFIED TOOL RESULT",
        "-" * 25,
        verified_result,
        "",
        "MANAGEMENT RESPONSE",
        "-" * 25,
        management_response,
        "",
        "IMPORTANT NOTE",
        "-" * 25,
        (
            "The numerical findings were calculated using "
            "Python tools. Explanations and recommendations "
            "generated by the language model must be reviewed "
            "by a qualified person before use."
        )
    ]

    return "\n".join(
        report_lines
    )


# --------------------------------------------------
# RESET RESULTS
# --------------------------------------------------

def reset_results():
    """
    Clear previous agent results when a new CSV is uploaded.
    """

    keys_to_remove = [
        "operations_dataframe",
        "operations_csv_text",
        "selected_tool",
        "verified_result",
        "management_response",
        "last_question",
        "stakeholder_email"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


# --------------------------------------------------
# APPLICATION HEADING
# --------------------------------------------------

st.title(
    "Local AI Operations Copilot"
)

st.write(
    "Upload operational KPI data and ask business questions. "
    "The local AI router selects an analytical tool, Python "
    "calculates verified results and Mistral produces a "
    "management explanation and stakeholder email."
)

st.info(
    "This application separates numerical calculations "
    "from language-model interpretation. Python calculates "
    "the figures, while the local language model explains "
    "the findings and drafts business communications."
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

try:
    with st.spinner(
        "Loading the local Mistral model..."
    ):
        llm = load_language_model()

except Exception as error:
    st.error(
        "The local language model could not be loaded."
    )

    st.code(
        str(error)
    )

    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header(
        "Agent Configuration"
    )

    st.write(
        "Language model"
    )

    st.code(
        "mistral"
    )

    st.write(
        "Orchestration framework"
    )

    st.code(
        "LangChain"
    )

    st.write(
        "Available analytical tools"
    )

    st.markdown(
        """
- KPI Summary
- Monthly Trend
- Cancellation Analysis
- Completion Analysis
        """
    )

    st.divider()

    st.caption(
        "All model processing runs locally through Ollama."
    )


# --------------------------------------------------
# CSV UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload operational KPI data",
    type=["csv"],
    on_change=reset_results
)


if uploaded_file is not None:
    try:
        dataframe = pd.read_csv(
            uploaded_file
        )

        is_valid, validation_message = (
            validate_dataframe(
                dataframe
            )
        )

        if not is_valid:
            st.error(
                validation_message
            )

        else:
            st.session_state[
                "operations_dataframe"
            ] = dataframe

            st.session_state[
                "operations_csv_text"
            ] = dataframe.to_csv(
                index=False
            )

            st.success(
                "The operational data was loaded and "
                "validated successfully."
            )

            st.subheader(
                "Data Preview"
            )

            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True
            )

            (
                preview_column_1,
                preview_column_2,
                preview_column_3
            ) = st.columns(3)

            with preview_column_1:
                st.metric(
                    "Periods",
                    len(dataframe)
                )

            with preview_column_2:
                st.metric(
                    "Total Jobs Raised",
                    f"{int(dataframe['JobsRaised'].sum()):,}"
                )

            with preview_column_3:
                st.metric(
                    "Total Jobs Cancelled",
                    f"{int(dataframe['JobsCancelled'].sum()):,}"
                )

    except Exception as error:
        st.error(
            "The CSV file could not be processed."
        )

        st.code(
            str(error)
        )


# --------------------------------------------------
# BUSINESS QUESTION
# --------------------------------------------------

st.divider()

st.subheader(
    "Ask the Operations Copilot"
)

business_question = st.text_input(
    "Enter a business question",
    placeholder=(
        "Example: Why are cancellations increasing?"
    )
)


if st.button(
    "Run Agent Analysis",
    type="primary",
    use_container_width=True
):
    if "operations_csv_text" not in st.session_state:
        st.error(
            "Please upload a valid operational CSV first."
        )

    elif not business_question.strip():
        st.error(
            "Please enter a business question."
        )

    else:
        try:
            with st.spinner(
                "The AI router is selecting an analytical tool..."
            ):
                selected_tool = select_tool(
                    business_question,
                    llm
                )

            with st.spinner(
                "Python is calculating verified results..."
            ):
                verified_result = (
                    execute_selected_tool(
                        selected_tool,
                        st.session_state[
                            "operations_csv_text"
                        ]
                    )
                )

            with st.spinner(
                "Mistral is preparing the management response..."
            ):
                management_response = (
                    generate_management_response(
                        business_question,
                        selected_tool,
                        verified_result,
                        llm
                    )
                )

            st.session_state[
                "selected_tool"
            ] = selected_tool

            st.session_state[
                "verified_result"
            ] = verified_result

            st.session_state[
                "management_response"
            ] = management_response

            st.session_state[
                "last_question"
            ] = business_question

            st.session_state.pop(
                "stakeholder_email",
                None
            )

            st.success(
                "The agent workflow completed successfully."
            )

        except Exception as error:
            st.error(
                "The agent workflow failed."
            )

            st.code(
                str(error)
            )

            st.info(
                "Confirm that Ollama is running and that "
                "Mistral appears in 'ollama list'."
            )


# --------------------------------------------------
# DISPLAY AGENT RESULTS
# --------------------------------------------------

if st.session_state.get(
    "management_response"
):
    selected_tool = st.session_state[
        "selected_tool"
    ]

    verified_result = st.session_state[
        "verified_result"
    ]

    management_response = st.session_state[
        "management_response"
    ]

    last_question = st.session_state[
        "last_question"
    ]

    st.divider()

    st.subheader(
        "Agent Decision"
    )

    decision_column_1, decision_column_2 = (
        st.columns(2)
    )

    with decision_column_1:
        st.metric(
            "Selected Tool",
            selected_tool
        )

    with decision_column_2:
        st.metric(
            "Workflow Status",
            "Completed"
        )

    st.subheader(
        "Verified Python Result"
    )

    st.code(
        verified_result,
        language="json"
    )

    st.subheader(
        "Management Analysis"
    )

    st.markdown(
        management_response
    )

    st.warning(
        "Review all generated explanations and recommendations. "
        "The language model cannot prove operational causes "
        "that are not present in the uploaded data."
    )

    management_report = create_management_report(
        last_question,
        selected_tool,
        verified_result,
        management_response
    )

    st.download_button(
        label="Download Management Report",
        data=management_report,
        file_name="operations_agent_report.txt",
        mime="text/plain",
        use_container_width=True
    )

    # ----------------------------------------------
    # STAKEHOLDER EMAIL GENERATOR
    # ----------------------------------------------

    st.divider()

    st.subheader(
        "Stakeholder Email Generator"
    )

    st.write(
        "Generate a professional email using the verified "
        "Python result and management analysis."
    )

    if st.button(
        "Generate Stakeholder Email",
        use_container_width=True
    ):
        try:
            with st.spinner(
                "Mistral is drafting the stakeholder email..."
            ):
                stakeholder_email = (
                    generate_stakeholder_email(
                        last_question,
                        selected_tool,
                        verified_result,
                        management_response,
                        llm
                    )
                )

            st.session_state[
                "stakeholder_email"
            ] = stakeholder_email

            st.success(
                "The stakeholder email was generated."
            )

        except Exception as error:
            st.error(
                "The stakeholder email could not be generated."
            )

            st.code(
                str(error)
            )

    if st.session_state.get(
        "stakeholder_email"
    ):
        edited_email = st.text_area(
            "Review and edit the stakeholder email",
            value=st.session_state[
                "stakeholder_email"
            ],
            height=400
        )

        st.warning(
            "Review all figures and wording before sending "
            "the email to stakeholders."
        )

        st.download_button(
            label="Download Stakeholder Email",
            data=edited_email,
            file_name="stakeholder_email.txt",
            mime="text/plain",
            use_container_width=True
        )


# --------------------------------------------------
# SUGGESTED QUESTIONS
# --------------------------------------------------

st.divider()

st.subheader(
    "Suggested Questions"
)

st.markdown(
    """
- What are the overall operational KPIs?
- How did performance change from January to June?
- Why are cancellations increasing?
- Which month had the highest cancellation volume?
- How has the completion rate changed?
- Which period had the strongest completion performance?
    """
)


# --------------------------------------------------
# AGENT WORKFLOW
# --------------------------------------------------

st.divider()

st.subheader(
    "Agent Workflow"
)

st.code(
    """
Business Question
        ↓
Local Mistral Tool Router
        ↓
Select Specialised Analytical Tool
        ↓
Python Executes Verified Calculations
        ↓
Verified JSON Result
        ↓
Local Mistral Management Explanation
        ↓
Local Mistral Stakeholder Email
        ↓
Reviewable and Downloadable Outputs
    """
)

st.info(
    "This proof of concept uses an AI routing pattern. "
    "The language model selects a specialised Python tool, "
    "but Python performs all numerical calculations."
)