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
