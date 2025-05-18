# GitHub Copilot Instructions for smart-invest

## Project Context

# Project Prompt


## Best Practices

No best practices provided.


## Recommended VS Code Extensions

No extensions suggested.


## Documentation Sources

No documentation sources provided.




## Best Practices


- Modular Design: Structure the application into well-defined, reusable modules for data fetching, analysis, prediction, reporting, and storage to enhance maintainability and testability.

- Data Validation with Pydantic: Utilize Pydantic extensively for validating API responses, configuration data, and internal data structures, ensuring data integrity throughout the application.

- Robust Error Handling & Logging: Implement comprehensive try-except blocks for error handling and use structured logging (e.g., Python's `logging` module) to record application behavior, errors, and important events for easier debugging and monitoring.

- Configuration Management: Externalize all configurations (API keys, database URLs, email settings, GCS paths) using environment variables and `.env` files, managed securely with Pydantic's `BaseSettings`.

- Automated Testing: Develop a comprehensive test suite using `pytest`, including unit tests for individual functions/modules and integration tests for workflows like data processing, prediction logic, and API interactions. Aim for high test coverage.

- CI/CD with GitHub Actions: Automate the entire development lifecycle, including linting, formatting, testing, building, and the scheduled execution of the data analysis and reporting job using GitHub Actions.

- Modern Dependency Management: Employ Poetry or PDM for robust dependency management, ensuring reproducible builds and a clean project environment.

- Asynchronous Operations for I/O: Leverage `asyncio` along with `httpx` for non-blocking I/O operations, especially when fetching data from multiple external APIs, to improve performance and responsiveness.

- Database Schema Management: Use Alembic for managing SQLAlchemy database migrations, allowing for version-controlled and systematic updates to the SQLite database schema.

- Secure Credential Management: Store and manage sensitive information like API keys and GCS credentials securely using GitHub Secrets for Actions and a secure method for local development (e.g., environment variables, Doppler, or HashiCorp Vault). Avoid hardcoding credentials.




## Recommended VS Code Extensions


- ms-python.python

- ms-python.pylance

- charliermarsh.ruff

- eamodio.gitlens

- ms-azuretools.vscode-docker

- streetsidesoftware.code-spell-checker

- visualstudioexptteam.vscodeintellicode

- redhat.vscode-yaml

- esbenp.prettier-vscode




## Documentation Sources


- Python Official Documentation: https://docs.python.org/3/

- Pydantic Documentation: https://docs.pydantic.dev/latest/

- PydanticAI Documentation: https://pydantic.github.io/pydantic-ai/

- SQLAlchemy Documentation (v2.0): https://docs.sqlalchemy.org/en/20/

- Alembic Documentation: https://alembic.sqlalchemy.org/en/latest/

- Pandas Documentation: https://pandas.pydata.org/pandas-docs/stable/

- WeasyPrint Documentation (for PDF generation): https://weasyprint.org/

- ReportLab User Guide (alternative for PDF generation): https://www.reportlab.com/docs/reportlab-userguide.pdf

- GitHub Actions Documentation: https://docs.github.com/en/actions

- Google Cloud Storage Client Libraries for Python: https://cloud.google.com/python/docs/reference/storage/latest

- HTTPX Documentation (for async HTTP requests): https://www.python-httpx.org/

- Requests Documentation (for sync HTTP requests): https://requests.readthedocs.io/en/latest/

- Scikit-learn Documentation: https://scikit-learn.org/stable/

- Poetry Documentation (Dependency Management): https://python-poetry.org/docs/

- PDM Documentation (Alternative Dependency Management): https://pdm-project.org/latest/

- Ruff Linter/Formatter Documentation: https://docs.astral.sh/ruff/




## Project-Specific Guidelines


- Use asynchronous programming with `asyncio` and `httpx` for efficient data fetching.

- Implement robust error handling and logging throughout the application.

- Employ Pydantic for rigorous data validation at all stages.

- Structure the code into well-defined modules for maintainability.

- Utilize Alembic for database schema management.

- Write comprehensive unit and integration tests using `pytest`.

- Configure GitHub Actions for automated testing, building, and deployment.

- Securely manage API keys and credentials using GitHub Secrets.

- Prioritize code readability and maintainability.

- Follow PEP 8 style guidelines and use Ruff for linting and formatting.




## Helpful Context


- Python Official Documentation: https://docs.python.org/3/

- Pydantic Documentation: https://docs.pydantic.dev/latest/

- PydanticAI Documentation: https://pydantic.github.io/pydantic-ai/

- SQLAlchemy Documentation (v2.0): https://docs.sqlalchemy.org/en/20/

- Alembic Documentation: https://alembic.sqlalchemy.org/en/latest/

- Pandas Documentation: https://pandas.pydata.org/pandas-docs/stable/

- WeasyPrint Documentation (for PDF generation): https://weasyprint.org/

- ReportLab User Guide (alternative for PDF generation): https://www.reportlab.com/docs/reportlab-userguide.pdf

- GitHub Actions Documentation: https://docs.github.com/en/actions

- Google Cloud Storage Client Libraries for Python: https://cloud.google.com/python/docs/reference/storage/latest

- HTTPX Documentation (for async HTTP requests): https://www.python-httpx.org/

- Requests Documentation (for sync HTTP requests): https://requests.readthedocs.io/en/latest/

- Scikit-learn Documentation: https://scikit-learn.org/stable/

- Poetry Documentation (Dependency Management): https://python-poetry.org/docs/

- PDM Documentation (Alternative Dependency Management): https://pdm-project.org/latest/

- Ruff Linter/Formatter Documentation: https://docs.astral.sh/ruff/

