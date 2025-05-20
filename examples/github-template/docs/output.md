# Project Prompt

# smart-wise

**Organization:** HappyPathway

## Overview

smart-wise is a comprehensive personal wellness and productivity hub designed to empower users to take control of their health and well-being. It offers a suite of tools for tracking physical activity, managing nutrition, and receiving personalized coaching insights.

## Core Features

*   **Exercise Logging:** Track diverse physical activities (e.g., running, weightlifting, yoga), monitor progress (duration, distance, calories burned, personal records), and integrate with wearables (e.g., Apple Health, Google Fit).
*   **Nutrition Management:** Log meals with detailed nutritional information, analyze macronutrient and micronutrient intake, access a comprehensive food database (e.g., Open Food Facts, USDA), and set dietary goals.
*   **Personalized Coaching:** Receive data-driven insights, set personalized wellness goals (e.g., weight, activity levels, nutrition targets), and track progress through reports and visualizations.

## Desirable Features (Future Scope)

*   **Water Intake Tracking:** Log and monitor daily water consumption.
*   **Sleep Tracking:** Integrate with wearables or allow manual input to monitor sleep patterns and quality.
*   **Mindfulness Exercises:** Offer guided meditations, breathing exercises, and mindfulness resources.
*   **Recipe Suggestions:** Provide healthy recipe ideas based on dietary preferences and goals, possibly integrating with logged food items.

## Tech Stack

### Backend
*   **Language:** Python 3.11+
*   **Framework:** FastAPI (latest stable)
*   **Database:** PostgreSQL (latest stable)
*   **ORM:** SQLAlchemy 2.0+ (async with `asyncpg` driver)
*   **Migrations:** Alembic
*   **Data Validation:** Pydantic V2+
*   **Authentication:** OAuth2 with JWT (using `python-jose` and `passlib`)
*   **Async Tasks:** Celery (latest stable) with Redis or RabbitMQ as a message broker
*   **Caching:** Redis
*   **Testing:** Pytest, `pytest-asyncio`
*   **Dependency Management:** Poetry
*   **Deployment:** Docker, Kubernetes (target environment)

### Frontend (Mobile - Cross-Platform)
*   **Framework:** React Native (latest stable)
*   **Language:** TypeScript
*   **Navigation:** React Navigation (latest)
*   **State Management:** Redux Toolkit or Zustand
*   **UI Kits:** React Native Paper, NativeBase, or custom component library with a focus on UX.
*   **API Client:** Axios or TanStack Query/SWR for data fetching and caching.
*   **Wearable Integration:** `react-native-health` (Apple Health), `react-native-google-fit` (Google Fit), or explore newer unified APIs.
*   **Offline Storage:** AsyncStorage, WatermelonDB, or Realm for robust offline capabilities.
*   **Testing:** Jest, React Testing Library, Detox for E2E testing.

### Frontend (Web)
*   **Framework:** React 18+ (using Vite for project setup)
*   **Language:** TypeScript
*   **Routing:** React Router (latest)
*   **State Management:** Redux Toolkit or Zustand (consistent with mobile if possible).
*   **Styling:** Tailwind CSS, Material-UI (MUI), or a custom design system.
*   **API Client:** Axios or TanStack Query/SWR.
*   **Testing:** Jest, React Testing Library, Playwright or Cypress for E2E testing.

## Project Structure (Monorepo Recommended - e.g., using Nx or Turborepo)

```
smart-wise/
├── apps/
│   ├── backend/          # FastAPI application (Python)
│   ├── mobile-app/       # React Native application (TypeScript)
│   └── web-app/          # React web application (TypeScript)
├── packages/
│   ├── shared-types/     # TypeScript types/interfaces shared between frontends
│   └── ui-components/    # Shared React/React Native components (if applicable)
├── docs/                 # Project documentation (architecture, API, guides)
├── .github/              # GitHub specific files (workflows, issue templates, PR templates)
├── .gitignore
├── README.md
├── poetry.lock           # For backend (apps/backend/poetry.lock)
├── pyproject.toml        # For backend (apps/backend/pyproject.toml)
└── package.json          # Root package.json for monorepo tools / frontend workspaces
```

## Prerequisites

*   Node.js (latest LTS version - e.g., v18 or v20) and npm or yarn
*   Python (3.11+)
*   Poetry (for Python dependency management)
*   Docker and Docker Compose (for local development and deployment)
*   Access to a PostgreSQL instance (local or cloud-based)
*   (For Mobile Development) Setup for React Native development:
    *   Xcode (for iOS development on macOS)
    *   Android Studio (for Android development)
    *   Watchman, Ruby, Bundler (as per React Native docs)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart-wise
```

### 2. Backend Setup (`apps/backend`)

```bash
cd apps/backend
poetry install
poetry shell

# Create a .env file from .env.example and configure variables:
# DATABASE_URL=postgresql+asyncpg://user:password@host:port/database_name
# SECRET_KEY=your_very_strong_secret_key
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# ... other settings (e.g., Celery broker URL)

# Run database migrations (ensure DB is running and accessible)
alembic upgrade head

# Start the development server (FastAPI with Uvicorn)
uvicorn main:app --reload --port 8000
```
Access the API at `http://localhost:8000` and auto-generated API docs at `http://localhost:8000/docs`.

### 3. Frontend (Mobile) Setup (`apps/mobile-app`)

```bash
cd apps/mobile-app
npm install # or yarn install

# (iOS specific) Install pods
# cd ios && pod install && cd ..

# Create a .env file or config file for environment variables:
# API_BASE_URL=http://localhost:8000/api/v1 (or your machine's IP for physical device testing)

# Start the development server and run on simulator/device
npm run ios # or yarn ios
npm run android # or yarn android
```

### 4. Frontend (Web) Setup (`apps/web-app`)

```bash
cd apps/web-app
npm install # or yarn install

# Create a .env file (e.g., .env.local) for environment variables:
# VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start the development server (Vite)
npm run dev # or yarn dev
```
Access the web app, typically at `http://localhost:5173` (or as specified by Vite).

## Running Tests

### Backend (`apps/backend`)

```bash
poetry run pytest
```

### Frontend (Mobile - `apps/mobile-app`)

```bash
npm test # or yarn test
# For E2E tests (Detox), follow Detox setup and run commands.
```

### Frontend (Web - `apps/web-app`)

```bash
npm test # or yarn test
# For E2E tests (Playwright/Cypress), follow their respective setup and run commands.
```

## Linting and Formatting

### Backend (Python - `apps/backend`)

```bash
poetry run ruff check .
poetry run ruff format .
```

### Frontend (JavaScript/TypeScript - `apps/mobile-app` or `apps/web-app`)

```bash
npm run lint # or yarn lint
npm run format # or yarn format
```

## Building for Production

### Backend
Deployment will typically involve building a Docker image. Refer to `Dockerfile` (to be created) and CI/CD pipeline configurations.

### Frontend (Mobile)
Follow React Native official documentation for generating release builds for iOS App Store and Android Play Store.

### Frontend (Web)

```bash
cd apps/web-app
npm run build # or yarn build
```
This will create a `dist` folder with optimized static assets for deployment.

## Data Security and Compliance

This application handles Personal Health Information (PHI) and other sensitive user data. Adherence to robust security practices is paramount.
*   **Data Encryption:** All sensitive data must be encrypted both in transit (TLS/SSL) and at rest (database-level encryption, filesystem encryption).
*   **Authentication & Authorization:** Implement strong OAuth 2.0 based authentication with JWTs. Enforce role-based access control (RBAC) and principle of least privilege.
*   **Input Validation:** Rigorous server-side validation of all inputs (using Pydantic for backend).
*   **Dependency Management:** Regularly scan dependencies for vulnerabilities (e.g., `poetry show --outdated`, `npm audit`).
*   **Secure Headers:** Implement security headers (e.g., CSP, HSTS, X-Frame-Options) for the web application.
*   **Logging & Monitoring:** Implement comprehensive logging for security events and system activity. Monitor for suspicious activities.
*   **Compliance:** Design and operate with data privacy regulations in mind (e.g., GDPR, HIPAA). **Consult with legal and compliance experts to ensure all requirements are met.**

## Contribution Guidelines

Please refer to `CONTRIBUTING.md` (to be created). This document will outline coding standards, commit message conventions (e.g., Conventional Commits), pull request processes, and the development workflow.

## License

This project is licensed under the [Specify License - e.g., MIT License or Apache 2.0].
```


## Best Practices


- **Agile Development & Version Control:** Utilize Git with a clear branching strategy (e.g., GitFlow) and iterative development cycles (Scrum/Kanban).

- **Comprehensive Testing:** Implement a robust testing pyramid (Unit, Integration, E2E) for all application layers (Backend: Pytest; Frontend: Jest, React Testing Library, Detox/Playwright).

- **Security by Design:** Prioritize security throughout the development lifecycle. Adhere to OWASP Top 10, implement strong authentication (OAuth 2.0/JWT), encrypt sensitive data (at rest & in transit), and conduct regular security audits. Consider HIPAA/GDPR compliance if handling sensitive health data.

- **CI/CD & Automation:** Establish automated CI/CD pipelines (e.g., GitHub Actions, GitLab CI) for building, testing, and deploying applications to ensure rapid and reliable releases.

- **Code Quality & Maintainability:** Enforce strict linting (Ruff for Python, ESLint for TS/JS) and formatting (Ruff/Black for Python, Prettier for TS/JS). Use type hinting (Python type hints, TypeScript) extensively. Conduct regular code reviews.

- **Scalable Architecture:** Design for scalability using a well-structured modern framework for the backend (e.g., FastAPI with Python) and component-based architecture for frontends (React, React Native). Utilize containerization (Docker, Kubernetes) for deployment.

- **Asynchronous Programming:** Leverage asyncio in Python (FastAPI) for I/O-bound operations and async/await in JavaScript/TypeScript for non-blocking UI and API calls, enhancing performance and responsiveness.

- **Dependency Management:** Use modern dependency management tools (Poetry for Python, npm/yarn workspaces for JS/TS) to ensure reproducible builds and proactively manage vulnerabilities.

- **Comprehensive Documentation:** Maintain up-to-date documentation including API specifications (OpenAPI), architecture diagrams, setup guides, and clear code-level comments/docstrings.

- **User-Centric Design & Accessibility:** Focus on a user-friendly interface (UI) and positive user experience (UX). Ensure the application is accessible by adhering to WCAG or similar accessibility standards (A11y).



## Recommended VS Code Extensions


- ms-python.python (Python by Microsoft)

- ms-python.vscode-pylance (Pylance by Microsoft)

- charliermarsh.ruff (Ruff by Astral Software)

- dbaeumer.vscode-eslint (ESLint by Microsoft)

- esbenp.prettier-vscode (Prettier - Code formatter by Prettier)

- msjsdiag.vscode-react-native (React Native Tools by Microsoft)

- orta.vscode-jest (Jest by Orta)

- eamodio.gitlens (GitLens — Git supercharged by GitKraken)

- ms-azuretools.vscode-docker (Docker by Microsoft)

- rangav.vscode-thunder-client (Thunder Client by Ranga Vadhineni) or humao.rest-client (REST Client by Huachao Mao)

- PKief.material-icon-theme (Material Icon Theme by Philipp Kief)

- VisualStudioExptTeam.vscodeintellicode (IntelliCode by Microsoft)

- streetsidesoftware.code-spell-checker (Code Spell Checker by Street Side Software)



## Documentation Sources


- FastAPI Official Documentation: https://fastapi.tiangolo.com/

- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/

- Pydantic Documentation: https://docs.pydantic.dev/latest/

- Alembic Documentation: https://alembic.sqlalchemy.org/en/latest/

- React Native Official Documentation: https://reactnative.dev/docs/getting-started

- React Official Documentation: https://react.dev/learn

- TypeScript Official Documentation: https://www.typescriptlang.org/docs/

- Redux Toolkit Official Documentation: https://redux-toolkit.js.org/

- Zustand GitHub Repository: https://github.com/pmndrs/zustand

- React Navigation Documentation: https://reactnavigation.org/

- Vite Official Documentation: https://vitejs.dev/guide/

- Poetry Official Documentation: https://python-poetry.org/docs/

- Ruff Linter Documentation: https://docs.astral.sh/ruff/

- OWASP Top 10 Project: https://owasp.org/www-project-top-ten/

- Celery Project Documentation: https://docs.celeryq.dev/en/stable/




## GitHub Copilot Instructions
As GitHub Copilot, your role is to assist in the development of the 'smart-wise' personal wellness and productivity hub.

Project Overview:
- Backend: Python (FastAPI, SQLAlchemy, PostgreSQL)
- Frontend (Mobile): React Native, TypeScript
- Frontend (Web): React, TypeScript, Vite
- Core Features: Exercise logging, nutrition management, personalized coaching.
- Key Priorities: User-friendly UI, robust data security (HIPAA/GDPR considerations), cross-platform compatibility, scalability, maintainability.

Guidelines for Assistance:

1.  **Language and Framework Specificity:**
    *   For backend tasks, provide Python code compatible with FastAPI (latest stable), SQLAlchemy (2.0+ for async with `asyncpg`), and Pydantic (V2+). Emphasize async endpoints.
    *   For mobile frontend, generate React Native components using TypeScript, functional components with Hooks, and adhere to patterns from React Navigation (latest) and Redux Toolkit/Zustand.
    *   For web frontend, generate React (18+) components using TypeScript, functional components with Hooks, and integrate with Vite, React Router (latest), and Redux Toolkit/Zustand.

2.  **Best Practices:**
    *   **Security:** Prioritize secure coding practices. For API endpoints, include authentication (OAuth2 with JWT) and authorization checks. Sanitize inputs and outputs. Remind about OWASP Top 10 and data encryption (at rest and in transit).
    *   **Testing:** Generate boilerplate for Pytest (backend) and Jest/React Testing Library (frontend). Encourage comprehensive test coverage, including integration and E2E tests (Detox for mobile, Playwright/Cypress for web).
    *   **Typing:** Emphasize strong typing. Use Python type hints and TypeScript interfaces/types extensively.
    *   **Modularity:** Write modular and reusable code. Break down complex functions and components into smaller, manageable pieces.
    *   **Error Handling:** Implement robust error handling (e.g., custom exception handlers in FastAPI, error boundaries in React) and structured logging.
    *   **Asynchronous Operations:** Utilize `async/await` in Python (FastAPI) and JavaScript/TypeScript appropriately for I/O-bound and long-running tasks.
    *   **Readability:** Generate clean, well-commented, and readable code. Follow PEP 8 for Python (using Ruff/Black for formatting) and common TypeScript/React style guides (using Prettier).

3.  **Feature Implementation:**
    *   **Exercise Logging:** Suggest Pydantic and SQLAlchemy models for exercises, sets, reps, duration. Help with logic for progress tracking and potential wearable data synchronization.
    *   **Nutrition Management:** Assist with Pydantic and SQLAlchemy models for food items, meals, nutritional information (calories, macros, micros). Suggest integration points for food databases (e.g., Open Food Facts API).
    *   **Personalized Coaching:** Help structure algorithms or rules for generating insights based on user data. Suggest how to model goals and progress reports.
    *   **Wearable Integration (React Native):** Suggest how to structure calls to native modules or libraries like `react-native-health` (iOS) or `react-native-google-fit` (Android), or newer unified APIs if available.

4.  **API Design:**
    *   When generating FastAPI endpoints, follow RESTful principles. Use Pydantic for request/response validation and serialization.
    *   Include appropriate HTTP status codes and clear error responses. Ensure OpenAPI documentation is automatically generated and accurate.

5.  **Database Interaction (SQLAlchemy):**
    *   Generate SQLAlchemy 2.0 style models (e.g., using DeclarativeBase with type annotations) and asynchronous CRUD operations using `AsyncSession`.
    *   Remind about database migrations with Alembic, configured for async environments.

6.  **State Management (Frontend):**
    *   Provide examples for Redux Toolkit (slices, async thunks, selectors) or Zustand (stores, actions, selectors).

7.  **Code Snippets and Boilerplate:**
    *   Offer to generate boilerplate for new components, services, API endpoints, tests, and configuration files (e.g., `.env` templates, Dockerfiles).
    *   Suggest common utility functions (e.g., date manipulation, data transformation).

8.  **Documentation:**
    *   Encourage writing comprehensive docstrings for Python functions/classes/modules and JSDoc/TSDoc for frontend code.
    *   Help draft comments explaining complex logic or business rules.

Example Prompts for Copilot:
*   "Generate a FastAPI endpoint using async/await to log a new exercise session with Pydantic validation."
*   "Create SQLAlchemy 2.0 models and Pydantic V2 schemas for user nutrition logs, including macros."
*   "Write a React Native component using TypeScript to display daily calorie intake, fetching data via an async thunk with Redux Toolkit."
*   "Suggest a Pytest fixture for an async SQLAlchemy database session."
*   "How to implement OAuth2 password flow with JWT tokens in this FastAPI app?"
*   "Draft a TypeScript interface for aggregated daily health data from wearables."

By following these instructions, you will help maintain a high standard of code quality, security, and consistency across the smart-wise project.
