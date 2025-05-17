"""
# crm-webapp

**Organization:** HappyPathway
**Description:** A web application for customer relationship management with a React frontend and Node.js backend.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Tech Stack](#tech-stack)
3.  [Prerequisites](#prerequisites)
4.  [Getting Started](#getting-started)
    *   [Backend Setup](#backend-setup)
    *   [Frontend Setup](#frontend-setup)
5.  [Scripts](#scripts)
6.  [Project Structure (Recommended)](#project-structure-recommended)
7.  [Coding Guidelines](#coding-guidelines)
8.  [Testing](#testing)
9.  [API Documentation](#api-documentation)
10. [Environment Variables](#environment-variables)
11. [Deployment](#deployment)
12. [Contributing](#contributing)
13. [License](#license)

## 1. Project Overview

The crm-webapp is designed to provide a comprehensive solution for managing customer relationships. It features a modern, responsive user interface built with React and TypeScript, and a robust backend powered by Node.js (with Express.js or NestJS) and TypeScript.

Key Features (To be defined by HappyPathway):
*   Customer data management (CRUD operations)
*   Interaction logging and tracking
*   Sales pipeline visualization
*   User authentication and authorization
*   Reporting and analytics dashboards

## 2. Tech Stack

### Frontend
*   **Framework:** React (v18.2+)
*   **Language:** TypeScript (v5.x+)
*   **Build Tool:** Vite (v5.x+)
*   **State Management:** Zustand (v4.x+) or Redux Toolkit (v2.x+)
*   **Routing:** React Router (v6.x+)
*   **Styling:** Tailwind CSS (v3.x+) or Styled Components (v6.x+)
*   **UI Component Library (Optional):** Material-UI (MUI v5.x+), Ant Design (v5.x+)
*   **Form Handling:** React Hook Form (v7.x+)
*   **Data Fetching:** React Query (TanStack Query v5.x+) or RTK Query
*   **Testing:** Jest (v29.x+), React Testing Library (v14.x+)

### Backend
*   **Runtime:** Node.js (LTS version, e.g., v20.x+)
*   **Framework:** Express.js (v4.18.x+) or NestJS (v10.x+) (TypeScript-first)
*   **Language:** TypeScript (v5.x+)
*   **Database:** PostgreSQL (Recommended) or MongoDB
*   **ORM/ODM:** Prisma (v5.x+) for SQL, Mongoose (v8.x+) for MongoDB
*   **API Specification:** OpenAPI (Swagger) - auto-generated with NestJS or via tools like `swagger-jsdoc` for Express.
*   **Authentication:** Passport.js with JWT strategy
*   **Validation:** Zod, class-validator (for NestJS)
*   **Testing:** Jest (v29.x+), Supertest

### General
*   **Version Control:** Git & GitHub/GitLab/Bitbucket
*   **Package Managers:** npm (v10.x+) or Yarn (v1.22.x+ or Berry v4.x+)
*   **Linting/Formatting:** ESLint (v8.x+), Prettier (v3.x+)
*   **Containerization (Recommended):** Docker, Docker Compose
*   **CI/CD:** GitHub Actions, GitLab CI, Jenkins

## 3. Prerequisites

*   Node.js (LTS version - verify with `node -v`)
*   npm or Yarn (verify with `npm -v` or `yarn -v`)
*   Git (verify with `git --version`)
*   Docker and Docker Compose (Optional, but recommended for local development consistency - verify with `docker --version` and `docker-compose --version`)
*   A running instance of PostgreSQL or MongoDB if not using Docker for databases.

## 4. Getting Started

### Clone the Repository

```bash
git clone <repository-url>
cd crm-webapp
```

### Backend Setup

(Assuming backend code resides in a `backend/` directory)

```bash
cd backend
```

1.  **Install Dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

2.  **Environment Variables:**
    Copy the example environment file and customize it:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` with your database credentials, JWT secrets, API keys, port, etc. (See [Environment Variables](#environment-variables) section for details).

3.  **Database Setup & Migration (if using Prisma):**
    ```bash
    # Ensure your database server is running or use Docker Compose
    npx prisma migrate dev --name init_schema
    npx prisma db seed # If you have seed scripts
    ```
    For other ORMs/ODMs, follow their respective migration and seeding instructions.

4.  **Run the Backend Development Server:**
    ```bash
    npm run dev
    # or
    yarn dev
    ```
    The backend server will typically run on `http://localhost:3001` (or as configured in `.env`).

### Frontend Setup

(Assuming frontend code resides in a `frontend/` directory)

```bash
cd ../frontend # Navigate from backend or root to frontend
```

1.  **Install Dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

2.  **Environment Variables:**
    Copy the example environment file if it exists and customize it:
    ```bash
    cp .env.example .env # If applicable
    ```
    Edit `.env` to set `VITE_API_BASE_URL` (e.g., `VITE_API_BASE_URL=http://localhost:3001/api`).

3.  **Run the Frontend Development Server:**
    ```bash
    npm run dev
    # or
    yarn dev
    ```
    The frontend application will typically run on `http://localhost:5173` (Vite default) or `http://localhost:3000`.

## 5. Scripts

Commonly used scripts (defined in `package.json` files in `frontend/` and `backend/` directories):

### Backend (`backend/package.json`)
*   `dev`: Starts the development server with hot-reloading (e.g., using `nodemon` or NestJS CLI).
*   `build`: Compiles TypeScript to JavaScript (e.g., into a `dist` folder).
*   `start`: Runs the production build.
*   `test`: Runs unit and integration tests.
*   `test:watch`: Runs tests in watch mode.
*   `test:cov`: Runs tests and generates a coverage report.
*   `lint`: Lints the codebase using ESLint.
*   `format`: Formats the codebase with Prettier.
*   `prisma:migrate:dev`: Runs Prisma migrations in development.
*   `prisma:studio`: Opens Prisma Studio.

### Frontend (`frontend/package.json`)
*   `dev`: Starts the Vite development server.
*   `build`: Builds the application for production (outputs to `dist` folder).
*   `preview`: Serves the production build locally (Vite specific).
*   `test`: Runs tests using Jest/React Testing Library.
*   `test:watch`: Runs tests in watch mode.
*   `lint`: Lints the codebase using ESLint.
*   `format`: Formats the codebase with Prettier.

## 6. Project Structure (Recommended)

```
crm-webapp/
├── backend/                  # Node.js (Express/NestJS) application
│   ├── prisma/               # Prisma schema, migrations, seeds (if using Prisma)
│   │   └── schema.prisma
│   ├── src/
│   │   ├── app.module.ts     # Root module (NestJS)
│   │   ├── main.ts           # Application bootstrap (NestJS)
│   │   ├── config/           # Configuration (database, auth, etc.)
│   │   ├── modules/          # Feature modules (e.g., users, customers, products)
│   │   │   └── users/
│   │   │       ├── users.controller.ts
│   │   │       ├── users.service.ts
│   │   │       ├── users.module.ts
│   │   │       ├── dto/          # Data Transfer Objects
│   │   │       └── entities/     # Database entities/schemas
│   │   ├── common/           # Shared utilities, decorators, guards, interceptors
│   │   ├── auth/             # Authentication module (NestJS)
│   │   └── app.ts            # Main application setup (Express)
│   │   └── routes/           # Routes definition (Express)
│   ├── test/                 # E2E and unit tests (Jest)
│   ├── .env.example
│   ├── .eslintrc.js
│   ├── .prettierrc.json
│   ├── nest-cli.json         # NestJS CLI configuration
│   ├── package.json
│   └── tsconfig.json
├── frontend/                 # React (Vite) application
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── App.tsx           # Root React component
│   │   ├── main.tsx          # Application entry point
│   │   ├── assets/           # Images, fonts, etc.
│   │   ├── components/       # Reusable UI components (dumb/presentational)
│   │   │   └── common/         # General purpose common components
│   │   ├── features/         # Feature-based modules (e.g., auth, customers)
│   │   │   └── customers/
│   │   │       ├── components/ # Feature-specific components
│   │   │       ├── hooks/      # Feature-specific hooks
│   │   │       ├── pages/      # Feature-specific pages
│   │   │       ├── services/   # Feature-specific API calls
│   │   │       └── store/      # Feature-specific state management
│   │   ├── hooks/            # Global custom React hooks
│   │   ├── layouts/          # Layout components (e.g., MainLayout, AuthLayout)
│   │   ├── lib/              # External library configurations (e.g. axios instance)
│   │   ├── pages/            # Top-level page components (if not feature-based)
│   │   ├── providers/        # React Context providers
│   │   ├── routes/           # Frontend routing configuration
│   │   ├── services/         # Global API service calls
│   │   ├── store/            # Global state management (Zustand/Redux setup)
│   │   ├── styles/           # Global styles, theme configuration
│   │   ├── types/            # Global TypeScript type definitions
│   │   └── utils/            # Utility functions
│   ├── tests/                # Unit/integration tests (Jest, RTL)
│   ├── .env.example
│   ├── .eslintrc.js
│   ├── .prettierrc.json
│   ├── index.html            # Main HTML file (for Vite)
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts        # Vite configuration
├── .dockerignore
├── .editorconfig
├── .gitattributes
├── .gitignore
├── docker-compose.yml        # Docker Compose for local development (e.g., db, backend, frontend)
├── CONTRIBUTING.md
├── LICENSE.md
└── README.md
```

## 7. Coding Guidelines

*   **Language:** Use TypeScript consistently across both frontend and backend.
*   **Style:** Adhere to the ESLint and Prettier configurations. Run `npm run lint` and `npm run format` before committing changes.
*   **Naming Conventions:**
    *   Components (React): `PascalCase` (e.g., `UserProfile.tsx`)
    *   Files/Folders (non-components): `kebab-case` (e.g., `user-services.ts`, `auth-utils/`)
    *   Variables/Functions: `camelCase` (e.g., `fetchUserData`)
    *   Types/Interfaces: `PascalCase` (e.g., `interface CustomerDetails`)
    *   CSS classes (if not using utility-first like Tailwind): BEM or `camelCase`.
*   **Comments:** Write JSDoc comments for functions, classes, types, and complex logic.
*   **Error Handling:** Implement robust error handling. Use custom error classes where appropriate. APIs should return consistent error responses.
*   **API Design:** Follow RESTful principles or GraphQL best practices. Ensure APIs are versioned if necessary.
*   **Accessibility (A11Y):** Design and develop frontend components to meet WCAG 2.1 AA standards.
*   **Modularity:** Keep components, functions, and modules small and focused on a single responsibility.

## 8. Testing

*   **Unit Tests:** Test individual functions, components (React Testing Library), services, and controllers in isolation. Mock dependencies.
*   **Integration Tests:** Test interactions between different parts of the application (e.g., API endpoints with Supertest, service interactions).
*   **End-to-End Tests (Recommended):** Test full user flows using tools like Playwright or Cypress.

Run tests using `npm test` (or `yarn test`) in the respective `frontend/` and `backend/` directories. Strive for high test coverage and include tests in the CI pipeline.

## 9. API Documentation

*   **NestJS:** API documentation can be automatically generated using `@nestjs/swagger`. Access it typically at `/api-docs` or `/api/docs`.
*   **Express.js:** Use tools like `swagger-jsdoc` and `swagger-ui-express` to generate and serve OpenAPI documentation.

Ensure API documentation is kept up-to-date with any changes.

## 10. Environment Variables

Sensitive information and environment-specific configurations should be managed through environment variables.

### Backend (`backend/.env`)
```
NODE_ENV=development # development, test, production
PORT=3001

# Database (Example for PostgreSQL with Prisma)
DATABASE_URL="postgresql://user:password@localhost:5432/crmdb_dev?schema=public"

# Database (Example for MongoDB with Mongoose)
# MONGO_URI="mongodb://localhost:27017/crmdb_dev"

# Authentication
JWT_SECRET="your-super-strong-and-long-jwt-secret-key"
JWT_EXPIRES_IN="1d"

# Other API Keys or external service URLs
# THIRD_PARTY_API_KEY="your_api_key"
# CORS_ORIGIN="http://localhost:5173"
```

### Frontend (`frontend/.env` for Vite)
```
# Base URL for API calls
VITE_API_BASE_URL=http://localhost:3001/api

# Other public environment variables (prefixed with VITE_)
# VITE_GOOGLE_ANALYTICS_ID="UA-XXXXX-Y"
```
**Never commit actual `.env` files with sensitive data. Only commit `.env.example` files.**

## 11. Deployment

(This section should be updated based on the chosen hosting providers and CI/CD setup.)

1.  **Containerization:** Use Docker to containerize the frontend and backend applications for consistent environments.
2.  **CI/CD Pipeline:** Set up a CI/CD pipeline (e.g., GitHub Actions, GitLab CI) to automate:
    *   Linting and Formatting Checks
    *   Running Tests (Unit, Integration, E2E)
    *   Building Docker Images
    *   Pushing Images to a Container Registry (e.g., Docker Hub, AWS ECR, Google GCR)
    *   Deploying to Staging and Production environments.
3.  **Hosting:**
    *   **Frontend:** Static hosting (Vercel, Netlify, AWS S3/CloudFront, Azure Static Web Apps).
    *   **Backend:** PaaS (Heroku, AWS Elastic Beanstalk, Google App Engine), Container Orchestration (Kubernetes, AWS ECS, Google Kubernetes Engine), or Serverless Functions (AWS Lambda, Google Cloud Functions).
    *   **Database:** Managed database services (AWS RDS, Azure Database, Google Cloud SQL, MongoDB Atlas).
4.  **Environment Variables:** Configure environment variables securely in the hosting environment.

## 12. Contributing

Please read `CONTRIBUTING.md` for details on our code of conduct, development process, and how to submit pull requests. (A `CONTRIBUTING.md` file should be created with guidelines for commit messages, branching, PRs, etc.).

## 13. License

This project is licensed under the [Specify License, e.g., MIT License]. See the `LICENSE.md` file for details. (A `LICENSE.md` file should be created).
"""


## Best Practices
- **Component-Based Architecture (Frontend):** Utilize React's component model for modular, reusable UI elements. Design with clear separation of concerns (presentational vs. container components, or using hooks for logic).
- **Scalable State Management (Frontend):** Choose an appropriate state management solution. For complex applications, consider Zustand (for simplicity and minimal boilerplate) or Redux Toolkit (for robust, predictable state). Utilize React Context API for simpler, localized state needs.
- **Robust API Design (Backend):** Design RESTful APIs with clear, consistent naming conventions, proper HTTP verb usage (GET, POST, PUT, DELETE, PATCH), and meaningful status codes. Consider GraphQL for complex data fetching requirements. Document APIs using OpenAPI (Swagger).
- **Security First (Full Stack):** Implement security best practices throughout the application: input validation (client and server-side), output encoding, authentication (e.g., JWT, OAuth2), authorization (role-based access control), protection against common vulnerabilities (XSS, CSRF, SQL/NoSQL injection), secure dependency management (e.g., `npm audit`), and use HTTPS.
- **Comprehensive Testing (Full Stack):** Implement a multi-layered testing strategy: unit tests (Jest, React Testing Library for frontend; Jest for backend), integration tests (Supertest for API endpoints), and end-to-end tests (Playwright, Cypress). Aim for high test coverage and automate testing in CI/CD pipelines.
- **Consistent Code Style and Linting:** Enforce a consistent code style using ESLint and Prettier. Integrate these tools into the development workflow (e.g., pre-commit hooks) to catch errors and formatting issues early.
- **Version Control with Git:** Utilize Git for version control with a well-defined branching strategy (e.g., GitFlow or GitHub Flow). Write clear, concise commit messages.
- **Environment Configuration Management:** Manage environment-specific configurations (development, staging, production) securely using environment variables (e.g., via `.env` files loaded by `dotenv` or platform-native environment variable management). Never commit sensitive credentials to the repository.
- **Efficient Asynchronous Operations:** Handle asynchronous operations effectively using Promises and `async/await` in both Node.js (for I/O, database operations) and React (for API calls, side effects in `useEffect`).
- **Accessibility (A11Y) for Frontend:** Design and develop the React frontend with accessibility in mind from the start. Follow WCAG (Web Content Accessibility Guidelines) to ensure the application is usable by people with disabilities. Use semantic HTML and ARIA attributes where necessary.

## Recommended VS Code Extensions
- **dbaeumer.vscode-eslint:** Integrates ESLint into VS Code for real-time linting.
- **esbenp.prettier-vscode:** Provides Prettier code formatting support.
- **ms-vscode.vscode-typescript-next (or built-in TS support):** For enhanced TypeScript IntelliSense and language features.
- **VisualStudioExptTeam.vscodeintellicode:** AI-assisted IntelliSense.
- **eamodio.gitlens:** Supercharges Git capabilities within VS Code (blame, history, etc.).
- **ms-azuretools.vscode-docker:** For managing Docker containers, images, and Dockerfiles.
- **Prisma.prisma:** Adds syntax highlighting, formatting, auto-completion, and linting for Prisma schema files.
- **bradlc.vscode-tailwindcss (if using Tailwind CSS):** Provides IntelliSense for Tailwind CSS classes.
- **styled-components.vscode-styled-components (if using Styled Components):** Syntax highlighting and IntelliSense for styled-components.
- **msjsdiag.debugger-for-chrome (or built-in JavaScript Debugger):** For debugging React applications in Chrome.
- **ms-vscode.node-debug2 (or built-in JavaScript Debugger):** For debugging Node.js applications.
- **DotENV.dotenv-vscode:** Syntax highlighting for `.env` files.
- **WallabyJs.wallaby-vscode (Commercial with free tier for OSS):** Continuous testing directly in the editor.
- **firsttris.vscode-jest-runner:** Easy way to run and debug Jest tests.
- **GitHub.copilot (if subscribed):** AI pair programmer.

## Documentation Sources
- **React Official Documentation:** `https://react.dev/` - The primary resource for React, including hooks, context, and patterns.
- **Node.js Official Documentation:** `https://nodejs.org/en/docs/` - For Node.js runtime, modules, and APIs.
- **TypeScript Handbook:** `https://www.typescriptlang.org/docs/handbook/intro.html` - Comprehensive guide to TypeScript.
- **Express.js Official Documentation:** `https://expressjs.com/` - For building APIs with Express.js.
- **NestJS Official Documentation:** `https://docs.nestjs.com/` - For building efficient, scalable server-side applications with NestJS.
- **Vite Official Documentation:** `https://vitejs.dev/` - For frontend tooling, build process, and development server.
- **Zustand GitHub Repository & Docs:** `https://github.com/pmndrs/zustand` - For state management with Zustand.
- **Redux Toolkit Official Documentation:** `https://redux-toolkit.js.org/` - For state management with Redux Toolkit.
- **React Router Official Documentation:** `https://reactrouter.com/` - For client-side routing in React applications.
- **Tailwind CSS Documentation:** `https://tailwindcss.com/docs` - For utility-first CSS framework.
- **Styled Components Documentation:** `https://styled-components.com/docs` - For component-level styling.
- **Jest Official Documentation:** `https://jestjs.io/` - For JavaScript testing framework.
- **React Testing Library Documentation:** `https://testing-library.com/docs/react-testing-library/intro/` - For testing React components.
- **Prisma Documentation:** `https://www.prisma.io/docs/` - For Next-generation ORM for Node.js and TypeScript.
- **Mongoose Documentation:** `https://mongoosejs.com/docs/guide.html` - For MongoDB object modeling for Node.js.
- **OpenAPI Specification:** `https://www.openapis.org/` - For API design and documentation.
- **MDN Web Docs (Mozilla Developer Network):** `https://developer.mozilla.org/` - General web platform documentation (HTML, CSS, JavaScript, Web APIs).

## GitHub Copilot Instructions
"""
# GitHub Copilot Instructions for crm-webapp (React/Node.js/TypeScript)

## General
- Prioritize TypeScript for all new code to ensure type safety.
- Adhere to DRY (Don't Repeat Yourself) and SOLID principles.
- Generate code with modern JavaScript/TypeScript features (ES6+).
- Include JSDoc comments for functions, classes, types, and interfaces.
- Suggest and implement comprehensive error handling (try-catch blocks, error classes, consistent error responses for APIs).
- When generating code, consider performance implications and suggest optimizations where applicable.
- Ensure all generated code follows ESLint and Prettier rules configured for the project.

## Frontend (React with TypeScript & Vite)
- **Component Generation**: "Create a React functional component named [ComponentName] using TypeScript that [description]. Props should be defined in an interface named `[ComponentName]Props`."
    - Example: "Create a React functional component named `CustomerTable` using TypeScript that displays a list of customers. Props should be `customers` (an array of `Customer` objects) and `onSelectCustomer` (a callback function)."
- **Hook Usage**: "Implement a custom React Hook named `use[FunctionName]` using TypeScript for [functionality]."
    - Example: "Implement a custom React Hook named `useDebounce` using TypeScript that takes a value and a delay, returning the debounced value."
- **State Management (Zustand/Redux Toolkit)**: "Create a Zustand store slice for [feature] with state [state properties and types] and actions [action names and parameters]." or "Create a Redux Toolkit slice for [feature] using `createSlice`, defining initial state, reducers, and async thunks for [actions]."
    - Example: "Create a Zustand store slice for `contacts` with state `contactList: Contact[]`, `isLoading: boolean`, `error: string | null` and actions `fetchContacts`, `addContact`."
- **Styling (Tailwind CSS/Styled Components)**: "Style this React component using Tailwind CSS classes to achieve [visual description]." or "Write styled-components for this React component based on [visual description]."
- **Testing (Jest/React Testing Library)**: "Write unit tests for the [ComponentName] React component using Jest and React Testing Library to cover [scenarios, e.g., rendering, prop handling, event interactions]. Mock any external dependencies or API calls."
    - Example: "Write unit tests for the `LoginForm` component to cover successful login, failed login due to incorrect credentials, and input validation errors."
- **API Calls**: "Write a TypeScript function using `fetch` or `axios` to call the [HTTP method] `/api/[endpoint]` endpoint. Include request body type definition `[RequestType]` and response type definition `[ResponseType]`. Handle loading states and errors."

## Backend (Node.js with Express.js/NestJS & TypeScript)
- **Route Handlers (Express.js)**: "Create an Express.js route handler for `[HTTP method] /api/[resource]` using TypeScript. Validate request body/params using a library like Zod or Joi. The handler should interact with [Service/Model] to [perform action]."
    - Example: "Create an Express.js route handler for `POST /api/users`. Validate `name` (string), `email` (string, email format), `password` (string, min 8 chars). Use `UserService` to create a new user."
- **Controllers/Services (NestJS)**: "Generate a NestJS controller for `[ResourceName]` with CRUD operations (Create, Read, Update, Delete) using DTOs for request/response validation. Implement the corresponding service methods in `[ResourceName]Service`."
    - Example: "Generate a NestJS controller for `Leads` with methods for `createLead(dto: CreateLeadDto)`, `findAllLeads()`, `findOneLead(id: string)`, `updateLead(id: string, dto: UpdateLeadDto)`, `removeLead(id: string)`."
- **Middleware (Express.js/NestJS)**: "Create an Express.js middleware function using TypeScript for [functionality, e.g., authentication, logging]." or "Create a NestJS middleware for [functionality]."
    - Example: "Create an Express.js middleware function using TypeScript to verify a JWT token from the Authorization header."
- **Database Interaction (Prisma/Mongoose)**: "Write a Prisma query using TypeScript to [description, e.g., find a user by email, create a new product]." or "Define a Mongoose schema for `[ResourceName]` with fields [field names and types]. Implement a static method for [custom query]."
    - Example: "Write a Prisma query to fetch all active customers along with their recent orders (last 5)." or "Define a Mongoose schema for `Task` with fields: `title` (String, required), `description` (String), `status` (String, enum: ['todo', 'inprogress', 'done'], default: 'todo'), `dueDate` (Date)."
- **API Documentation (JSDoc/Swagger with NestJS)**: "Add JSDoc comments for this Express route handler, including `@param`, `@returns`, and example request/response. For NestJS, use `@ApiProperty`, `@ApiResponse`, etc., decorators for Swagger documentation."

## TypeScript Specifics
- "Define a TypeScript interface or type alias for [data structure name] with the following properties: [property: type, ...]."
    - Example: "Define a TypeScript interface `UserProfile` with properties: `id: string`, `username: string`, `email: string`, `isActive: boolean`, `lastLogin?: Date`."
- When dealing with external APIs or complex objects, suggest generating types/interfaces. 

## Security
- When generating database queries, use parameterized queries or ORM methods to prevent SQL injection. Highlight this. 
- For user input, always suggest validation (e.g., using Zod, Joi, class-validator) and sanitization where appropriate.
- Remind about secure handling of secrets and API keys (environment variables).

## Best Practices
- Encourage refactoring opportunities: "Refactor this code to improve readability/performance/maintainability by [specific suggestion, e.g., extracting a function, using a more efficient algorithm]."
- Suggest use of utility functions for common tasks.
"""

