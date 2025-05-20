# Project Prompt
# avi-biscuits: Positive Parenting Rewards & Behavior Coach

**Organization:** HappyPathway

## Overview

avi-biscuits is a tool designed to support parents and caregivers by providing guidance on positive reinforcement strategies for children. It helps track behaviors, understand potential triggers, and discover age-appropriate rewards and constructive responses. The application emphasizes evidence-based positive parenting techniques to foster a supportive environment for child development.

**This application is intended as a supportive tool and NOT a replacement for professional advice. Always consult with child development experts or pediatricians for specific concerns.**

## Ethical Considerations: A Positive Approach to Parenting

This project is founded on the principles of **positive parenting**. We explicitly move away from the concept of "punishments" and instead focus on:

*   **Positive Reinforcement:** Recognizing and rewarding desirable behaviors to encourage their repetition.
*   **Understanding Behavior:** Helping identify patterns, triggers, and environmental stimuli related to specific behaviors.
*   **Effective, Constructive Consequences:** Implementing natural and logical consequences that teach, rather than punish. This includes strategies like time-ins, redirection, and loss of privileges directly related to the behavior.
*   **Age-Appropriateness:** Ensuring all suggested rewards and responses are suitable for the child's developmental stage.
*   **Emotional Well-being:** Promoting strategies that build a child's self-esteem and strengthen the parent-child relationship.

**The system will NOT suggest or endorse any form of physical punishment, verbal shaming, or overly punitive measures.** The focus is on coaching and guidance towards positive interactions.

## Features

*   **Child Profiles:** Manage basic information for each child (e.g., name, age) to tailor suggestions.
*   **Behavior Logging:** Track specific behaviors (positive and challenging) with details like date, time, context, and potential triggers/stimuli.
*   **Intervention Tracking:** Record rewards given for positive behaviors and constructive responses to challenging behaviors.
*   **Effectiveness Rating:** Monitor how well different rewards and responses are working over time.
*   **Rewards System & Idea Bank:** Access a curated list of age-appropriate reward ideas (tangible and intangible).
*   **Positive Discipline Guidance:** Receive suggestions for constructive responses to challenging behaviors, based on positive parenting principles.
*   **Behavioral Analysis & Graphs:** Visualize behavior patterns and intervention effectiveness over time through charts and graphs.
*   **CLI Access:** Manage data and get quick insights directly from the command line.
*   **Single Page Application (SPA):** A user-friendly web interface for easy interaction and visualization.
*   **SQLite Database:** Local data storage.
*   **Google Cloud Storage (GCS) Sync:** Securely back up and sync the database file to GCS.

## Tech Stack

*   **Backend & CLI:**
    *   Python 3.10+
    *   FastAPI (for REST API)
    *   Pydantic (for data validation & settings)
    *   SQLAlchemy (for ORM with SQLite)
    *   Alembic (for database migrations)
    *   Typer (for CLI)
    *   Matplotlib/Plotly (for graphing)
    *   `google-cloud-storage` (for GCS sync)
*   **Frontend (SPA):**
    *   React (with Vite) or Vue.js/Svelte (to be decided)
    *   JavaScript/TypeScript
    *   Charting library (e.g., Plotly.js, Recharts, Chart.js)
    *   CSS Framework (e.g., Tailwind CSS, Material-UI)
*   **Database:** SQLite
*   **Version Control:** Git

## Prerequisites

*   Python 3.10 or higher
*   Node.js and npm/yarn (for frontend development)
*   Git
*   Google Cloud SDK (gcloud CLI) configured for GCS access (optional, for GCS sync)

## Project Structure (Suggested)

```
avi-biscuits/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app instance
│   │   ├── api/            # API routers/endpoints
│   │   ├── core/           # Config, core settings
│   │   ├── crud/           # CRUD operations for database
│   │   ├── models/         # Pydantic models
│   │   ├── schemas/        # SQLAlchemy models (or combine with Pydantic models)
│   │   ├── services/       # Business logic, parenting advice logic
│   │   └── db/             # Database session, base model
│   ├── tests/              # Pytest tests for backend
│   ├── alembic/            # Alembic migration scripts
│   ├── alembic.ini
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── Dockerfile          # Optional: for containerization
├── frontend/               # SPA (e.g., React/Vite project)
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...                 # Other frontend files
├── cli/
│   ├── main.py             # Typer CLI application
│   └── utils/              # CLI specific utilities
├── data/                   # Local SQLite database file, GCS credentials (gitignore this dir)
│   └── app.db
│   └── gcs_credentials.json # IMPORTANT: Add to .gitignore
├── docs/                   # Project documentation
├── scripts/                # Utility scripts (e.g., GCS sync script)
├── .gitignore
├── README.md
└── .env.example            # Environment variable template
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd avi-biscuits
```

### 2. Backend Setup (Python)

```bash
cd backend
# Recommended: Use Poetry
poetry install
# Or, if using venv and requirements.txt (generate with 'poetry export -f requirements.txt --output requirements.txt')
# python -m venv .venv
# source .venv/bin/activate  # On Windows: .venv\Scripts\activate
# pip install -r requirements.txt

# Setup environment variables (copy .env.example to .env and fill in)
cp .env.example .env
# Edit .env with your GCS bucket name, project ID, etc.

# Initialize and run database migrations
poetry run alembic upgrade head # or alembic upgrade head if not using poetry
```

### 3. Frontend Setup (SPA - Example for React/Vite)

```bash
cd ../frontend
npm install # or yarn install
```

### 4. Google Cloud Storage Setup (Optional, for DB Sync)

1.  Create a GCS bucket in your Google Cloud Project.
2.  Create a Service Account with permissions to read/write to this bucket (e.g., `Storage Object Admin` role for the specific bucket).
3.  Download the JSON key file for the service account.
4.  **IMPORTANT:** Store this JSON key file securely. You can place it in the `data/` directory (ensure `data/gcs_credentials.json` is in your `.gitignore` file) and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to its path, or configure it in the application settings.
    ```bash
    # Example for .env file
    GCS_BUCKET_NAME="your-gcs-bucket-name"
    GCS_PROJECT_ID="your-gcp-project-id"
    # GOOGLE_APPLICATION_CREDENTIALS="data/gcs_credentials.json" # if using this method
    ```

## Running the Application

### 1. Backend API Server

```bash
cd backend
poetry run uvicorn app.main:app --reload
# Or, if not using poetry:
# uvicorn app.main:app --reload
```

The API will typically be available at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`.

### 2. Frontend SPA (Development Server)

```bash
cd ../frontend
npm run dev # or yarn dev
```

Access the SPA in your browser, usually at `http://localhost:5173` (Vite default) or as indicated by the console output.

### 3. Command Line Interface (CLI)

```bash
cd ../cli
# Ensure backend virtual environment is active or use poetry run
poetry run python main.py --help
poetry run python main.py log-behavior --description "Completed homework without prompting" --type good --child-id 1
poetry run python main.py generate-report --child-id 1 --output-path reports/behavior_chart.png
```

## Usage Guide

### Single Page Application (SPA)

*   **Dashboard:** Overview of recent behaviors and reward effectiveness.
*   **Children:** Add and manage child profiles (name, age).
*   **Log Behavior:** Record new behavior incidents, including context, stimuli, and type (positive/challenging).
*   **Log Intervention:** Document rewards applied for positive behaviors or constructive responses to challenging ones. Rate their perceived effectiveness.
*   **Insights & Graphs:** View trends, frequency charts, and effectiveness of interventions over time.
*   **Resource Hub:** Access articles and tips on positive parenting, age-appropriate rewards, and constructive discipline techniques (this section will link to or summarize research).

### Command Line Interface (CLI)

The CLI provides quick access to core functionalities:

*   `add-child --name <name> --age <age>`
*   `log-behavior --child-id <id> --description "..." --type <good/challenging> --stimulus "..."`
*   `log-intervention --behavior-id <id> --intervention-type <reward/consequence> --description "..." --effectiveness <1-5>`
*   `list-behaviors --child-id <id>`
*   `suggest-reward --child-id <id> --behavior-type <type>`
*   `suggest-consequence --child-id <id> --behavior-description "..."`
*   `generate-report --child-id <id> --output-path <path.png>`
*   `sync-db --direction <upload/download>` (for GCS sync)

Refer to `python cli/main.py --help` for detailed commands and options.

## Database

*   **Schema:** The database schema will include tables for children, behavior events, interventions, reward ideas, and consequence ideas. Relationships will link these entities.
*   **Migrations:** Alembic is used for managing database schema changes. To create a new migration: `poetry run alembic revision -m "create_some_table"`. To apply migrations: `poetry run alembic upgrade head`.
*   **GCS Sync:** The SQLite database file (`data/app.db`) can be synced with Google Cloud Storage. This can be triggered via the CLI or potentially automated. Ensure credentials are secure and the bucket is private.

## Parenting Guidance Research

This application will incorporate principles from reputable sources on child development and positive parenting, such as:

*   American Academy of Pediatrics
*   Child Mind Institute
*   Positive Discipline Association

Key principles include:

*   **Focus on connection before correction.**
*   **Use encouragement and praise generously and specifically.**
*   **Understand the 'why' behind behavior.**
*   **Teach problem-solving skills.**
*   **Set clear and consistent boundaries.**
*   **Model desired behaviors.**

## Testing

*   **Backend:** Pytest is used for unit and integration tests. Run tests with `poetry run pytest` in the `backend` directory.
*   **Frontend:** Jest and React Testing Library (or equivalent for other frameworks) will be used. Run tests with `npm test` (or `yarn test`) in the `frontend` directory.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes, ensuring adherence to ethical guidelines and coding standards.
4.  Write tests for your changes.
5.  Commit your changes (`git commit -m 'Add some feature'`).
6.  Push to the branch (`git push origin feature/your-feature-name`).
7.  Open a Pull Request.

## License

(To be determined - e.g., MIT, Apache 2.0). Consider the sensitive nature of the data if distributing widely.

---

**Disclaimer:** This tool is for informational and tracking purposes only. It is not a substitute for professional advice from pediatricians, child psychologists, or other qualified professionals. Always consult with experts for guidance on your child's specific needs and behaviors.
```


## Best Practices


- **Ethical Design First:** Prioritize positive, evidence-based parenting techniques. Reframe 'punishments' to 'effective consequences' or 'positive discipline strategies'. Consult child development experts or resources if possible. Ensure data privacy and security, especially for sensitive information about children.

- **Backend - FastAPI for APIs:** Use FastAPI for building the Python backend API. Its native Pydantic integration, automatic data validation, and OpenAPI documentation generation are highly beneficial. Current stable version: ~0.111.0.

- **Data Modeling with Pydantic & SQLAlchemy:** Define clear Pydantic models for request/response validation and SQLAlchemy 2.0.x models for database interaction. Use Alembic for database schema migrations. Pydantic V2 (~2.7.1) offers significant performance improvements.

- **Frontend - Modern SPA Framework:** Develop the Single Page Application using a modern JavaScript/TypeScript framework like React (v18.x) with Vite (v5.x) for a fast development experience, or Vue.js (v3.x) / Svelte (v4.x).

- **CLI - Typer for User-Friendly Interface:** Implement the Command Line Interface using Typer for its ease of use and automatic help generation. Current stable version: ~0.12.3.

- **Robust Testing Strategy:** Implement comprehensive unit and integration tests for both backend (Pytest) and frontend (e.g., Jest, React Testing Library). Aim for high test coverage.

- **Dependency and Environment Management:** Use Poetry or PDM for Python dependency management and virtual environments. For frontend, use npm or yarn.

- **Version Control with Git:** Use Git for version control and host the repository on a platform like GitHub or GitLab. Follow a consistent branching strategy (e.g., GitFlow or GitHub Flow).

- **Code Quality & Formatting:** Enforce code style consistency using tools like Black and Ruff for Python, and Prettier/ESLint for JavaScript/TypeScript. Integrate these into pre-commit hooks.

- **Secure GCS Synchronization:** Implement Google Cloud Storage synchronization carefully. Use service accounts with least privilege access. Ensure the SQLite file is not corrupted during sync. Consider encryption at rest in GCS and in transit.



## Recommended VS Code Extensions


- ms-python.python (Python language support)

- ms-python.vscode-pylance (Enhanced Python IntelliSense)

- ms-python.flake8 (or use ruff extension: charliermarsh.ruff)

- charliermarsh.ruff (Python linter and formatter - recommended)

- njpwerner.autodocstring (Python docstring generator)

- VisualStudioExptTeam.vscodeintellicode (AI-assisted development)

- eamodio.gitlens (Git supercharged)

- esbenp.prettier-vscode (For frontend JavaScript/TypeScript formatting)

- dbaeumer.vscode-eslint (For frontend JavaScript/TypeScript linting)

- ms-azuretools.vscode-docker (If using Docker for containerization)

- TabNine.tabnine-vscode (AI code completion, alternative/complement to Copilot)

- cweijan.vscode-database-client2 (For viewing SQLite DB, or similar SQLite browser extension)



## Documentation Sources


- **Parenting & Child Development (Crucial for Ethical Design):**

- American Academy of Pediatrics: https://www.healthychildren.org

- Child Mind Institute: https://childmind.org

- Positive Discipline Association: https://www.positivediscipline.org

- CDC Essentials for Parenting Toddlers and Preschoolers: https://www.cdc.gov/parents/essentials/index.html

- 

- **Python & Backend:**

- Python Official Documentation: https://docs.python.org/3/

- FastAPI: https://fastapi.tiangolo.com/

- Pydantic: https://docs.pydantic.dev/

- SQLAlchemy: https://www.sqlalchemy.org/ (specifically SQLAlchemy 2.0)

- Alembic: https://alembic.sqlalchemy.org/

- Typer: https://typer.tiangolo.com/

- Google Cloud Storage Python Client: https://cloud.google.com/python/docs/reference/storage/latest

- Matplotlib: https://matplotlib.org/stable/contents.html

- Plotly (Python): https://plotly.com/python/

- Ruff (Linter & Formatter): https://docs.astral.sh/ruff/

- Black (Formatter): https://black.readthedocs.io/

- Pytest (Testing): https://docs.pytest.org/

- Poetry (Dependency Management): https://python-poetry.org/docs/

- 

- **Frontend (if using React/Vite):**

- React: https://react.dev/

- Vite: https://vitejs.dev/

- Plotly.js: https://plotly.com/javascript/

- Chart.js: https://www.chartjs.org/docs/latest/

- ESLint: https://eslint.org/

- Prettier: https://prettier.io/docs/en/

- 

- **General:**

- Git Documentation: https://git-scm.com/doc

- Google Cloud CLI (gcloud): https://cloud.google.com/sdk/gcloud




## GitHub Copilot Instructions
As GitHub Copilot, your role is to assist in developing the 'avi-biscuits' project. Focus on:
1.  **Ethical AI and Content:** When generating suggestions related to parenting advice, rewards, or consequences, strictly adhere to positive, evidence-based, and age-appropriate parenting techniques. Avoid any suggestions that could be construed as harmful, punitive, or shaming. Emphasize positive reinforcement and constructive guidance.
2.  **Python Backend (FastAPI):**
    *   Help create Pydantic models for data validation (e.g., `BehaviorEvent`, `ChildProfile`, `Intervention`).
    *   Assist in developing SQLAlchemy ORM models and relationships.
    *   Guide the creation of FastAPI routes (endpoints) for CRUD operations on behaviors, rewards, etc.
    *   Help implement business logic for suggesting rewards/consequences based on stored data and parenting principles.
3.  **CLI Development (Typer):**
    *   Assist in structuring CLI commands for logging behaviors, managing profiles, and generating reports.
    *   Help integrate graphing functionalities (e.g., using Matplotlib to save charts).
4.  **GCS Integration:**
    *   Provide snippets for uploading and downloading the SQLite database file to/from Google Cloud Storage using the `google-cloud-storage` library.
    *   Help with error handling and authentication for GCS operations.
5.  **Frontend (React with Vite - if assisting with JS/TS):**
    *   Suggest component structures for displaying behavior logs, graphs, and reward/consequence suggestions.
    *   Help with API calls to the FastAPI backend.
    *   Assist in integrating a charting library like Plotly.js or Recharts.
6.  **Best Practices:** Remind the developer about Python type hinting, writing docstrings, unit tests (Pytest), and using environment variables for configuration (e.g., GCS credentials).
7.  **Data Analysis and Graphing:** Assist in writing functions to process behavioral data and prepare it for graphing (e.g., trends over time, frequency of behaviors).
