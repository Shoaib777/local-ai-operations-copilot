# Local AI Operations Copilot

A locally hosted agent-style business analytics application built with Python, Streamlit, LangChain, Ollama and Mistral.

The application accepts operational CSV data, uses a local AI router to select an appropriate analytical tool, performs verified KPI calculations in Python, generates a management analysis and creates a professional stakeholder email.

## Key Features

- Operational CSV upload and validation
- Local AI-powered tool selection
- Four specialised analytical tools
- Verified Python KPI calculations
- Monthly trend analysis
- Cancellation analysis
- Completion-rate analysis
- Management insight generation
- Stakeholder email generation
- Downloadable management reports
- Local open-weight language model
- Human-review and responsible-AI controls

## Available Analytical Tools

### KPI Summary

Calculates:

- Total jobs raised
- Total jobs completed
- Total jobs cancelled
- Total unresolved jobs
- Overall completion rate
- Overall cancellation rate

### Monthly Trend Analysis

Compares the first and final reporting periods, including:

- Jobs raised
- Jobs completed
- Jobs cancelled
- Completion-rate changes
- Cancellation-rate changes
- Unresolved workload

### Cancellation Analysis

Identifies:

- Highest cancellation period
- Highest cancellation rate
- Cancellation growth
- First-period and final-period comparisons

### Completion Analysis

Identifies:

- Highest completion volume
- Highest completion rate
- Lowest completion rate
- Completion-rate movement

## Agent Workflow

```text
Business Question
        |
        v
Local Mistral Tool Router
        |
        v
Select Specialised Analytical Tool
        |
        v
Python Executes Verified Calculations
        |
        v
Verified JSON Result
        |
        v
Mistral Management Explanation
        |
        v
Mistral Stakeholder Email
        |
        v
Reviewable and Downloadable Outputs
```

## Technology Stack

- Python
- Streamlit
- pandas
- LangChain
- langchain-ollama
- Ollama
- Mistral
- Local LLM inference

## Installation

### 1. Install Ollama

Download and install Ollama, then download Mistral:

```bash
ollama pull mistral
```

Confirm the model is available:

```bash
ollama list
```

### 2. Create a Python environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Required CSV Structure

The uploaded CSV must contain:

```text
Month
JobsRaised
JobsCompleted
JobsCancelled
```

A sample file is available at:

```text
data/operations.csv
```

## Example Questions

- What are the overall operational KPIs?
- How did performance change from January to June?
- Why are cancellations increasing?
- Which month had the highest cancellation volume?
- How has the completion rate changed?
- Which period had the strongest completion performance?

## Responsible AI

Python performs all numerical calculations. The language model selects an analytical tool and explains the verified output.

The language model is instructed not to invent operational causes. Possible explanations must be treated as areas for investigation rather than proven conclusions.

All generated analysis, recommendations and stakeholder emails must be reviewed before business use.

## Skills Demonstrated

- Agentic AI workflow design
- LangChain orchestration
- AI-based tool routing
- Tool-using AI patterns
- Local LLM integration
- Open-weight language models
- Python analytics
- Data validation
- KPI calculation
- Prompt engineering
- Business insight generation
- Automated stakeholder communication
- Human-review controls
- Streamlit application development

## Project Status

Completed self-directed AI engineering portfolio project.