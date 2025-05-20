# Project Prompt

# smart-invest
**Organization:** HappyPathway

## 1. Overview

`smart-invest` is a Python-based application designed for automated analysis of trade and investment data. It leverages publicly available APIs and databases to gather financial information, employs AI (specifically Google's Gemini model via `instructor` and Google Search) for data interpretation and insight generation, predicts market patterns, and generates daily PDF reports. These reports, which include a self-assessment of past prediction accuracy, are then emailed to subscribers. The entire process is orchestrated to run as a cron job using GitHub Actions, with data persistence managed via SQLite and Google Cloud Storage (GCS).

## 2. Features

- **Automated Data Ingestion**: Fetches financial data from various public APIs and databases.
- **Data Analysis**: Performs analysis on trade and investment data.
- **AI-Powered Insights**: Uses Pydantic with `instructor` to query Google's Gemini model and Google Search for data enrichment, analysis, and generating textual summaries or insights.
- **Pattern Prediction**: Implements models to predict potential market patterns. (Initial scope may involve simpler models, with capability to expand).
- **Prediction Tracking & Self-Grading**: Stores historical investment predictions and their outcomes, automatically grading its prediction accuracy over time.
- **Dynamic PDF Reporting**: Generates daily PDF reports summarizing analysis, predictions, AI-generated insights, and historical prediction accuracy.
- **Email Notifications**: Distributes the generated PDF reports to a list of subscribers.
- **Scheduled Execution**: Runs automatically on a defined schedule (e.g., daily) using GitHub Actions cron jobs.
- **Persistent Storage**: Utilizes SQLite for local data storage (predictions, accuracy history, configurations), with the database file synchronized with Google Cloud Storage (GCS) for persistence across job runs.
- **Modular Architecture**: Designed with multiple components (agents/models) working in concert for different tasks like data fetching, analysis, LLM interaction, prediction, and reporting.

## 3. Architecture

The system is designed as a series of interconnected modules orchestrated by a main application script, which is triggered by GitHub Actions:

1.  **Orchestrator (GitHub Actions)**:
    *   Runs on a cron schedule.
    *   Sets up the Python environment and installs dependencies.
    *   **GCS Sync (Pull)**: Downloads the latest SQLite database from GCS.
    *   Executes the main application logic.
    *   **GCS Sync (Push)**: Uploads the updated SQLite database to GCS.

2.  **Data Ingestion Module**:
    *   Fetches raw data from configured public financial APIs (e.g., stock prices, economic indicators, news feeds).
    *   Uses `httpx` for efficient HTTP requests.
    *   Validates incoming data using Pydantic models.

3.  **LLM Integration Module (`instructor` with Gemini & Google Search)**:
    *   Uses `instructor` to get Pydantic-validated structured output from Google's Gemini model.
    *   Queries Gemini for data analysis, summarization, sentiment analysis, or generating narrative insights based on fetched data.
    *   Utilizes Google Search API to find relevant recent news, articles, or specific data points to augment analysis.
    *   Pydantic models define the expected schema for LLM responses.

4.  **Data Storage Module (SQLAlchemy & SQLite)**:
    *   Defines database schema using SQLAlchemy ORM.
    *   Stores fetched data, analysis results, prediction parameters, historical predictions, actual outcomes, and accuracy scores in a SQLite database.
    *   Alembic can be used for schema migrations.

5.  **Analysis & Prediction Engine**:
    *   **Analysis Core**: Processes and analyzes the fetched data.
    *   **Pattern Prediction Models**: Implements one or more algorithms to predict future patterns or trends. This can range from statistical methods to machine learning models.
    *   Predictions are stored along with the rationale or key factors, potentially derived from LLM insights.

6.  **Self-Assessment Module (Historian)**:
    *   Retrieves past predictions from the database.
    *   Compares them with actual market outcomes (fetched or manually updated).
    *   Calculates accuracy scores (e.g., MAPE, directional accuracy).
    *   Updates the database with these scores.
    *   This feedback loop is crucial for iterative improvement and transparent reporting.

7.  **Reporting Engine (PDF Generation)**:
    *   Uses a library like WeasyPrint to convert HTML/CSS templates into PDF reports.
    *   Templates are populated with data including: market summary, new predictions, AI-generated insights, historical prediction performance (including accuracy grade).

8.  **Notification Module (Email)**:
    *   Sends the generated PDF reports to a predefined list of subscribers.
    *   Uses `smtplib` for sending emails.

## 4. Tech Stack

- **Programming Language**: Python (3.10+ recommended, ideally 3.11 or 3.12)
- **Data Validation & Settings**: Pydantic (v2)
- **LLM Interaction**: `instructor` (for Pydantic + LLMs), `google-generativeai` (for Gemini API), `google-api-python-client` (for Google Search API)
- **Database**: SQLite
- **ORM**: SQLAlchemy (v2.x)
- **Database Migrations**: Alembic (optional, but recommended for schema evolution)
- **Cloud Storage**: Google Cloud Storage (GCS) via `google-cloud-storage` library
- **HTTP Client**: `httpx` (preferred for async capabilities) or `requests`
- **PDF Generation**: WeasyPrint (recommended), ReportLab, or FPDF
- **Email**: `smtplib` (Python standard library)
- **Dependency Management**: Poetry
- **Linting/Formatting**: Ruff
- **Testing**: Pytest
- **CI/CD & Scheduling**: GitHub Actions
- **Potential ML Libraries (for advanced prediction)**: Scikit-learn, Statsmodels, Prophet, TensorFlow/Keras, PyTorch

## 5. Prerequisites

- Python (see Tech Stack for version)
- A Google Cloud Platform (GCP) account with:
    - A GCS bucket created.
    - Service account credentials (JSON keyfile) with permissions to read/write to the GCS bucket.
- API Keys for:
    - Google AI Studio (for Gemini API).
    - Google Cloud Console (for Google Search API, if a custom search engine is used, or other Google APIs).
    - Any financial data APIs being used.
- Email account credentials (SMTP server, port, username, password) for sending reports.

## 6. Project Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/HappyPathway/smart-invest.git
    cd smart-invest
    ```

2.  **Install Python**: Ensure you have a compatible Python version installed. (e.g., Python 3.11 from `https://www.python.org/downloads/`)

3.  **Setup Poetry**: If not already installed, install Poetry:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
    (Follow official Poetry installation instructions for your OS: `https://python-poetry.org/docs/#installation`)

4.  **Install Dependencies**: Poetry will create a virtual environment and install dependencies from `pyproject.toml` and `poetry.lock`.
    ```bash
    poetry install
    ```

5.  **Configuration (`.env` file)**:
    Create a `.env` file in the project root. This file is ignored by Git (`.gitignore` should list `.env`). Populate it with necessary credentials and configurations. Pydantic's `BaseSettings` will load these.

    Example `.env` file:
    ```env
    # GCP Configuration
    GCP_PROJECT_ID="your-gcp-project-id"
    GCS_BUCKET_NAME="your-smart-invest-gcs-bucket"
    GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-service-account-key.json"

    # Gemini API Key
    GEMINI_API_KEY="your_gemini_api_key"

    # Google Search API (example, specific keys depend on setup)
    GOOGLE_SEARCH_API_KEY="your_google_search_api_key"
    GOOGLE_SEARCH_CX="your_custom_search_engine_id"

    # Financial APIs (example)
    ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key"

    # Email Configuration
    SMTP_HOST="smtp.example.com"
    SMTP_PORT=587
    SMTP_USERNAME="your_email@example.com"
    SMTP_PASSWORD="your_email_password"
    EMAIL_SENDER="smart-invest@example.com"
    EMAIL_SUBSCRIBERS="subscriber1@example.com,subscriber2@example.com"

    # Application Settings
    DATABASE_URL="sqlite:///./smart_invest.db" # Path to the local SQLite file
    LOG_LEVEL="INFO"
    ```

6.  **GCS Setup**:
    *   Create a GCS bucket in your GCP project.
    *   Download the JSON service account key and update `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file or set it as an environment variable in GitHub Actions secrets.

7.  **Database Initialization (if using Alembic)**:
    If you're using Alembic for migrations:
    ```bash
    poetry run alembic upgrade head
    ```
    Otherwise, SQLAlchemy will create the tables based on model definitions on first run if designed to do so.

## 7. Configuration Details

Application configuration is managed via Pydantic's `BaseSettings` class, which loads values from environment variables (and the `.env` file for local development).

Key configuration variables (refer to `.env` example):
- `GCP_PROJECT_ID`, `GCS_BUCKET_NAME`, `GOOGLE_APPLICATION_CREDENTIALS`
- `GEMINI_API_KEY`
- `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_CX` (if applicable)
- Financial API keys (e.g., `ALPHA_VANTAGE_API_KEY`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `EMAIL_SENDER`, `EMAIL_SUBSCRIBERS` (comma-separated list)
- `DATABASE_URL` (e.g., `sqlite:///./data/smart_invest.db`)
- `LOG_LEVEL` (e.g., `INFO`, `DEBUG`)

These will be defined in a `config.py` module using Pydantic.

## 8. Usage

### Local Execution

To run the application locally (e.g., for testing a full cycle):

```bash
poetry run python main.py
```
(Assuming `main.py` is your main application script.)

### GitHub Actions Workflow

The application is designed to run automatically via a GitHub Actions workflow defined in `.github/workflows/daily_run.yml`.

Key aspects of the workflow:
- **Trigger**: Cron schedule (e.g., `cron: '0 8 * * *'` for daily at 8 AM UTC).
- **Secrets**: All API keys, GCS credentials, and email passwords must be stored as GitHub Encrypted Secrets (e.g., `GCP_SA_KEY_B64` (base64 encoded JSON), `GEMINI_API_KEY`, `SMTP_PASSWORD`).
- **Steps**:
    1.  Checkout repository.
    2.  Set up Python.
    3.  Install Poetry and dependencies (`poetry install --no-root --no-dev`).
    4.  Authenticate to Google Cloud (e.g., using `google-github-actions/auth`).
    5.  Download SQLite DB from GCS.
    6.  Run the main application script (`poetry run python main.py`).
    7.  Upload updated SQLite DB to GCS.

## 9. Modules Overview (Conceptual)

- **`smart_invest/`**
    - **`main.py`**: Main application script, orchestrates the workflow.
    - **`config.py`**: Pydantic settings management.
    - **`core/`**: Core logic and shared utilities.
        - **`logger.py`**: Logging setup.
    - **`data_sources/`**: Modules for fetching data from various APIs.
        - `public_api_client.py`
    - **`gcs/`**: GCS interaction logic.
        - `client.py` (upload/download DB)
    - **`database/`**: SQLAlchemy models, session management, CRUD operations.
        - `models.py`
        - `crud.py`
        - `session.py`
    - **`llm/`**: Integration with Gemini and Google Search via `instructor`.
        - `client.py` (Gemini client setup)
        - `prompts.py`
        - `schemas.py` (Pydantic models for LLM output)
        - `services.py` (functions to query LLMs)
    - **`analysis/`**: Data analysis logic.
        - `analyzer.py`
    - **`prediction/`**: Prediction models and logic.
        - `models/` (different prediction model implementations)
        - `predictor.py`
    - **`reporting/`**: PDF report generation.
        - `generator.py`
        - `templates/` (HTML/CSS templates for PDF)
    - **`notifications/`**: Emailing service.
        - `emailer.py`
    - **`history/`**: Prediction tracking and self-grading logic.
        - `assessor.py`
- **`tests/`**: Pytest tests for all modules.
- **`scripts/`**: Utility scripts (e.g., one-off tasks, backfills).
- **`alembic/`**: (If using Alembic) migration scripts.
- **`.github/workflows/`**: GitHub Actions workflows.
    - `daily_run.yml`
- **`pyproject.toml`**: Project metadata and dependencies for Poetry.
- **`.env.example`**: Template for environment variables.

## 10. Development

- **Linting & Formatting**: Uses Ruff. Configure in `pyproject.toml` or `ruff.toml`.
  ```bash
  poetry run ruff check . --fix
  poetry run ruff format .
  ```
- **Testing**: Uses Pytest. Tests are located in the `tests/` directory.
  ```bash
  poetry run pytest
  ```
- **Pre-commit Hooks**: Consider setting up pre-commit hooks to automate linting/formatting before commits.

## 11. Error Handling and Logging

- Implement robust error handling, especially for network requests, API interactions, and data processing.
- Use structured logging (e.g., JSON format) to make logs easier to parse and analyze, especially in GitHub Actions.

## 12. Security Considerations

- **Never commit secrets** (API keys, passwords, GCP service account keys) to the repository.
- Use GitHub Encrypted Secrets for CI/CD pipelines.
- For local development, use `.env` files and add `.env` to `.gitignore`.
- Regularly review GCP IAM permissions for the service account.
- Be mindful of rate limits for all external APIs.

## 13. Future Enhancements

- More sophisticated prediction models (e.g., ML-based).
- Interactive web dashboard for viewing reports and historical data.
- User authentication for accessing reports or managing subscriptions.
- More data sources and types of analysis.
- Advanced anomaly detection.
- Backtesting framework for prediction models.

---
This document provides a comprehensive guide for the `smart-invest` project. For specific technical details, refer to the linked documentation for each tool and library.
"""


## Best Practices


- Modular Design: Structure the application into loosely coupled modules (data fetching, analysis, prediction, reporting, LLM interaction, etc.) for better maintainability, testability, and scalability. Each 'agent' or 'model' can be a distinct module.

- Dependency Management: Utilize Poetry for robust dependency management, ensuring reproducible builds and a clear project structure. Commit the `poetry.lock` file.

- Configuration Management: Externalize all configurations (API keys, GCS bucket details, email settings, model parameters) using environment variables. Leverage Pydantic's `BaseSettings` for loading, validating, and type-hinting configurations.

- Data Validation with Pydantic: Employ Pydantic extensively for validating incoming data from external APIs, database integrity, configuration values, and ensuring structured, typed outputs from LLM interactions (using `instructor` with Gemini).

- Automated Testing: Implement comprehensive unit and integration tests using Pytest. Focus on testing data processing pipelines, prediction logic, LLM interactions, report generation, and the self-grading mechanism.

- CI/CD with GitHub Actions: Automate linting (Ruff), testing, and the daily cron job execution using GitHub Actions. Securely manage all secrets (API keys, GCS credentials) using GitHub Encrypted Secrets.

- Robust Logging: Implement structured logging throughout the application (e.g., using the standard `logging` module configured for JSON output) to facilitate debugging and monitoring of the cron jobs.

- Idempotent GCS Synchronization: Ensure that the process of pulling the SQLite database from GCS and pushing it back is idempotent and handles potential race conditions or failures gracefully, especially in a cron job environment.

- SQLAlchemy and Alembic: Use SQLAlchemy 2.0 for ORM interactions with the SQLite database. Implement Alembic for database schema migrations to manage changes to the database structure over time.

- Ethical AI and Data Usage: When using Gemini and Google Search, be mindful of rate limits, terms of service, and the ethical implications of interpreting and reporting AI-generated information, especially for financial predictions.



## Recommended VS Code Extensions


- ms-python.python

- ms-python.vscode-pylance

- charliermarsh.ruff

- njpwerner.autodocstring

- eamodio.gitlens

- GitHub.copilot

- redhat.vscode-yaml

- esbenp.prettier-vscode



## Documentation Sources


- Python Official Documentation: https://docs.python.org/3/

- Pydantic: https://docs.pydantic.dev/latest/

- Instructor (Pydantic with LLMs): https://python.useinstructor.com/

- Google AI Python SDK (Gemini): https://ai.google.dev/docs/sdk / https://github.com/google/generative-ai-python

- Google API Python Client (for Google Search, etc.): https://github.com/googleapis/google-api-python-client

- Google Cloud Storage Python Client: https://cloud.google.com/python/docs/reference/storage/latest

- SQLAlchemy (Core and ORM): https://docs.sqlalchemy.org/en/20/

- Alembic (Database Migrations for SQLAlchemy): https://alembic.sqlalchemy.org/en/latest/

- WeasyPrint (HTML/CSS to PDF): https://weasyprint.readthedocs.io/en/stable/

- ReportLab (PDF Generation): https://www.reportlab.com/docs/reportlab-userguide.pdf

- HTTPLib (`httpx` - async HTTP client): https://www.python-httpx.org/

- Requests (HTTP client): https://requests.readthedocs.io/en/latest/

- GitHub Actions: https://docs.github.com/en/actions

- Ruff (Linter & Formatter): https://docs.astral.sh/ruff/

- Poetry (Dependency Management): https://python-poetry.org/docs/

- Pytest (Testing Framework): https://docs.pytest.org/en/stable/

- Standard Library `smtplib` (Email): https://docs.python.org/3/library/smtplib.html

- Standard Library `email.mime`: https://docs.python.org/3/library/email.mime.html




## GitHub Copilot Instructions
# GitHub Copilot Instructions for smart-invest

## Project Context



## Best Practices


- Modular Design: Structure the application into loosely coupled modules (data fetching, analysis, prediction, reporting, LLM interaction, etc.) for better maintainability, testability, and scalability. Each 'agent' or 'model' can be a distinct module.

- Dependency Management: Utilize Poetry for robust dependency management, ensuring reproducible builds and a clear project structure. Commit the `poetry.lock` file.

- Configuration Management: Externalize all configurations (API keys, GCS bucket details, email settings, model parameters) using environment variables. Leverage Pydantic's `BaseSettings` for loading, validating, and type-hinting configurations.

- Data Validation with Pydantic: Employ Pydantic extensively for validating incoming data from external APIs, database integrity, configuration values, and ensuring structured, typed outputs from LLM interactions (using `instructor` with Gemini).

- Automated Testing: Implement comprehensive unit and integration tests using Pytest. Focus on testing data processing pipelines, prediction logic, LLM interactions, report generation, and the self-grading mechanism.

- CI/CD with GitHub Actions: Automate linting (Ruff), testing, and the daily cron job execution using GitHub Actions. Securely manage all secrets (API keys, GCS credentials) using GitHub Encrypted Secrets.

- Robust Logging: Implement structured logging throughout the application (e.g., using the standard `logging` module configured for JSON output) to facilitate debugging and monitoring of the cron jobs.

- Idempotent GCS Synchronization: Ensure that the process of pulling the SQLite database from GCS and pushing it back is idempotent and handles potential race conditions or failures gracefully, especially in a cron job environment.

- SQLAlchemy and Alembic: Use SQLAlchemy 2.0 for ORM interactions with the SQLite database. Implement Alembic for database schema migrations to manage changes to the database structure over time.

- Ethical AI and Data Usage: When using Gemini and Google Search, be mindful of rate limits, terms of service, and the ethical implications of interpreting and reporting AI-generated information, especially for financial predictions.




## Recommended VS Code Extensions


- ms-python.python

- ms-python.vscode-pylance

- charliermarsh.ruff

- njpwerner.autodocstring

- eamodio.gitlens

- GitHub.copilot

- redhat.vscode-yaml

- esbenp.prettier-vscode




## Documentation Sources


- Python Official Documentation: https://docs.python.org/3/

- Pydantic: https://docs.pydantic.dev/latest/

- Instructor (Pydantic with LLMs): https://python.useinstructor.com/

- Google AI Python SDK (Gemini): https://ai.google.dev/docs/sdk / https://github.com/google/generative-ai-python

- Google API Python Client (for Google Search, etc.): https://github.com/googleapis/google-api-python-client

- Google Cloud Storage Python Client: https://cloud.google.com/python/docs/reference/storage/latest

- SQLAlchemy (Core and ORM): https://docs.sqlalchemy.org/en/20/

- Alembic (Database Migrations for SQLAlchemy): https://alembic.sqlalchemy.org/en/latest/

- WeasyPrint (HTML/CSS to PDF): https://weasyprint.readthedocs.io/en/stable/

- ReportLab (PDF Generation): https://www.reportlab.com/docs/reportlab-userguide.pdf

- HTTPLib (`httpx` - async HTTP client): https://www.python-httpx.org/

- Requests (HTTP client): https://requests.readthedocs.io/en/latest/

- GitHub Actions: https://docs.github.com/en/actions

- Ruff (Linter & Formatter): https://docs.astral.sh/ruff/

- Poetry (Dependency Management): https://python-poetry.org/docs/

- Pytest (Testing Framework): https://docs.pytest.org/en/stable/

- Standard Library `smtplib` (Email): https://docs.python.org/3/library/smtplib.html

- Standard Library `email.mime`: https://docs.python.org/3/library/email.mime.html




## Project-Specific Guidelines

- Follow best practices for Python development.
- Use standard conventions for Automated Data Analysis, AI-Powered Prediction, and Reporting System projects.
- Implement secure coding practices and proper error handling.
- Add appropriate documentation and comments.



## Helpful Context

- Consider the overall project architecture and design patterns.

