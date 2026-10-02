# AI Interview Generator

An AI-powered interview practice platform built with **Python, Streamlit, Google Gemini, SQLite, and ReportLab**. It generates personalized interview questions, evaluates candidate answers using AI-generated rubrics, provides detailed feedback, stores interview history, and creates downloadable PDF reports.

## Overview

The AI Interview Generator is designed to make interview preparation more structured and personalized. A candidate enters their target job role, skills, experience level, difficulty level, interview type, and number of questions. The application then uses Google Gemini to create a customized interview.

Each generated question receives its own evaluation rubric. Candidate answers are evaluated against these rubrics, and the application produces question-wise scores, strengths, missing concepts, feedback, ideal answers, and an overall interview result.

## Features

- Personalized AI-generated interview questions
- Role, skill, experience, difficulty, and interview-type based customization
- AI-generated evaluation rubric for every question
- Candidate answer evaluation with a score out of 10
- Strengths and missing-concept analysis
- Detailed AI feedback and ideal answers
- Overall interview score, percentage, and performance summary
- Previous/next question navigation during interviews
- Interview history stored using SQLite
- Reopen completed interview reports
- Downloadable PDF interview reports
- Streamlit-based responsive user interface
- Friendly error handling for API and application failures

## How It Works

```text
Candidate Details
       |
       v
AI Question Generation
       |
       v
AI Rubric Generation
       |
       v
Candidate Answers Questions
       |
       v
AI Answer Evaluation
       |
       v
Score + Strengths + Missing Concepts
+ Feedback + Ideal Answer
       |
       v
Final Result + Interview History + PDF Report
```

The application uses separate AI prompts for:

1. **Question Generation** — creates interview questions relevant to the selected role, skills, experience, difficulty, and interview type.
2. **Rubric Generation** — creates a structured 10-mark evaluation rubric for each question.
3. **Answer Evaluation** — evaluates the candidate's response using the stored rubric and generates detailed feedback.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Core application and backend logic |
| Streamlit | Web application interface |
| Google Gemini | Question generation, rubric generation, and answer evaluation |
| SQLite | Interview history and evaluation storage |
| ReportLab | PDF interview report generation |
| python-dotenv | Environment variable and API-key loading |

## Project Structure

```text
AI_Interview_Generator/
|
|-- app.py                  # Streamlit UI and application routing
|-- services.py             # Interview generation/evaluation service layer
|-- llm.py                  # Google Gemini API integration
|-- prompts.py              # LLM prompts
|-- database.py             # SQLite database operations
|-- utils.py                # Parsing and validation utilities
|-- requirements.txt        # Python dependencies
|-- .gitignore              # Files excluded from Git
|
|-- .streamlit/
|   `-- config.toml         # Streamlit configuration
|
|-- assets/
|   |-- welcome_robot.png
|   `-- sidebar_robot.png
|
`-- data/
    `-- interview.db        # Created/used locally and ignored by Git
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd AI_Interview_Generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The project requires:

```text
streamlit
python-dotenv
google-genai
reportlab
```

## Gemini API Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The application reads the key from the `GEMINI_API_KEY` environment variable.

> **Security:** Never upload your real `.env` file or Gemini API key to GitHub. The project `.gitignore` excludes `.env`.

## Run the Application

From the project directory, run:

```bash
python -m streamlit run app.py
```

Streamlit will display the local application URL in the terminal. Open it in your browser to start using the platform.

## Using the Application

1. Enter your name and continue to the interview setup.
2. Select the target **job role**.
3. Enter the relevant **skills**.
4. Choose the **experience level**.
5. Select the **difficulty level** and **interview type**.
6. Choose the **number of questions**.
7. Start the AI interview and wait while the questions and evaluation rubrics are generated.
8. Answer each interview question and submit your response.
9. Complete the interview to view the final result.
10. Review question-wise scores, strengths, missing concepts, feedback, and ideal answers.
11. Download the interview result as a **PDF report**.
12. Use **Interview History** to reopen previously completed reports.

## Evaluation System

Each interview question is assigned an AI-generated rubric with a maximum score of **10 marks**. The rubric considers factors such as:

- Technical correctness
- Important concepts
- Completeness
- Reasoning
- Clarity
- Practical understanding, where applicable

The evaluation result is stored in SQLite and contributes to the candidate's final score and percentage.

## PDF Reports

Completed interviews can be exported as PDF reports using ReportLab. The report includes:

- Candidate and interview details
- Overall score
- Percentage
- Performance summary
- Question-wise candidate answers
- Individual question scores
- Strengths
- Missing concepts/improvements
- AI feedback
- Ideal answers

## Interview History

The application stores interviews locally in SQLite. Completed interviews can be reopened from the **Interview History** page using the **View Report** option.

The local database is excluded from Git so that test data and local interview history are not committed to the repository.

## Screenshots

Add screenshots of the completed application here before final submission if desired.

Suggested screenshots:

- Welcome page
- Interview setup page
- AI interview/question page
- Final results page
- Interview history page
- Downloaded PDF report

Example:

```markdown
![Welcome Page](screenshots/welcome.png)
![Interview Setup](screenshots/setup.png)
![Results Page](screenshots/results.png)
```

## Future Scope

Possible future enhancements include:

- User authentication and individual candidate accounts
- Resume-based question generation
- Voice-based interview practice
- Speech-to-text candidate answers
- Behavioral and HR interview analysis
- Coding interview support
- Cloud database integration
- Analytics dashboard for long-term performance tracking
- Deployment for multi-user access

## Security Notes

- Keep `.env` private.
- Never commit API keys to GitHub.
- Local SQLite interview data should remain excluded from version control.
- If an API key is ever accidentally committed publicly, revoke/rotate it immediately.

## Project Purpose

This project demonstrates how Large Language Models can be integrated into a practical interview-preparation system. It combines personalized question generation, rubric-based AI evaluation, persistent interview history, performance analysis, and report generation in a single Python application.

## Version

**Version 1.0**

---

Built as an **AI-Based Interview Question Generator and Evaluation System** using Python and Google Gemini.
