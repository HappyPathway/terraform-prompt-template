# Template Generator Module for Terraform GitHub Project

## Overview

This module provides an interface between Terraform and Google's Gemini API for generating project documentation and templates. It leverages a Python script (`gemini_generator.py`) that uses Gemini's generative AI capabilities through a structured Pydantic AI agent implementation. The module writes both JSON and Markdown outputs directly to files for improved reliability and idempotency.

## Features

- Generate project documentation with Gemini AI
- Fetch existing templates from GitHub repositories
- Convert concrete values to placeholders for reusable templates
- Support for GitHub Enterprise through configurable API URLs
- Structured output format with error handling
- Google Search grounding for more accurate and current results (with Gemini 2.0+ models)
- Push generated templates to GitHub repositories
- Direct file output in both JSON and Markdown formats
- Improved reliability and idempotency with local file handling

## Supported Models

As of May 2025, the following Gemini models are supported:

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-2.5-pro-preview-05-06` | Latest 2.5 Pro preview (default) | Complex reasoning, advanced thinking |
| `gemini-2.5-flash-preview-04-17` | Latest 2.5 Flash preview | Efficient, adaptive thinking |
| `gemini-2.0-pro` | Latest stable 2.0 Pro | Complex reasoning tasks |
| `gemini-2.0-flash` | Latest stable 2.0 Flash | Speed and next-gen features |
| `gemini-2.0-flash-lite` | Lightweight 2.0 | Cost efficiency |
| `gemini-1.5-pro` | Stable 1.5 Pro | Complex reasoning fallback |
| `gemini-1.5-flash` | Stable 1.5 Flash | Fast and versatile fallback |

Search grounding is automatically enabled for Gemini 2.0+ models to provide the most current and accurate information.

## Usage

```hcl
module "template_generator" {
  source = "./modules/template_generator"

  # Required inputs
  project_prompt = "Create a web application for managing cloud infrastructure with React frontend and Go backend"
  project_name   = "cloud-manager"
  repo_org       = "my-organization"
  gemini_api_key = var.gemini_api_key  # Always use a variable for sensitive values
  
  # Optional: choose a specific model
  gemini_model   = "gemini-2.5-pro-preview-05-06"  # Default
  
  # Specify output directory for generated files
  template_dir   = "${path.module}/templates"

  # Optional: template formatting settings
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "${%s}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  
  # Optional: Configure token parameters
  model_settings = {
    temperature       = 0.2
    top_p             = 0.95
    top_k             = 40
    max_output_tokens = 16384
  }
  
  # Optional: GitHub API URL for Enterprise environments
  github_api_url = "https://github.example.com/api/v3"
  
  # Optional: Push to GitHub configuration
  push_to_github = true
  github_token   = var.github_token
  target_repo    = "my-org/my-templates"
  target_path    = "templates/my-project-template.json"
  target_branch  = "main"
}

# Access generated template content
locals {
  json_content = module.template_generator.generated_template_json
  markdown_content = module.template_generator.generated_template_markdown
  project_type = module.template_generator.project_type
}

# Create a local copy of the markdown file (optional, as the module already writes files)
resource "local_file" "template_markdown" {
  filename = "${path.module}/published/${local.project_type}-template.md"
  content  = local.markdown_content
}
```

### Example from the Repository

```hcl
module "template_generator_example" {
  source = "../.."
  
  # Required inputs
  project_prompt  = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name    = "crm-webapp"
  project_type    = "react-webapp"
  repo_org        = "HappyPathway" 
  gemini_api_key  = var.gemini_api_key
  gemini_model    = "google-gla:gemini-2.5-pro-preview-05-06"
  
  # Output directory
  template_dir = "${path.root}/templates"
  
  # Template configuration
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  
  # Disable search grounding for this example
  enable_search_grounding = false
}

# Output the results
output "template_generator" {
  description = "Generated markdown content"
  value       = module.template_generator_example.generated_template_markdown
}

# Save results to a file (optional, as the module already writes files)
resource local_file "generated_template" {
  filename = "${path.root}/templates/react-webapp.md"
  content  = module.template_generator_example.generated_template_markdown
}
```

## Running the Example

To run the included example:

1. Navigate to the example directory:
   ```bash
   cd examples/github-template
   ```

2. Set your Gemini API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Run Terraform:
   ```bash
   terraform apply
   ```

5. Check the generated files in the `templates` directory:
   ```bash
   ls -la templates/
   ```

The example will generate both JSON and Markdown files with the content created by the Gemini API.

## Google Search Grounding

Gemini 2.0+ models automatically use Google Search to ground responses in current facts from the web, ensuring that generated templates include:

- Up-to-date library and framework versions
- Current best practices and design patterns
- Latest documentation references and resources
- More factually accurate technical information

Search grounding is automatically enabled when using any Gemini 2.0 or 2.5 model. The module will:

1. Detect if the selected model supports search grounding
2. Automatically configure the appropriate search tools
3. Include search query information and sources in the output for verification
4. Expose search grounding usage via the `used_search_grounding` output variable

You can check if search grounding was used in your template generation:

```hcl
output "used_search_grounding" {
  value = module.template_generator.used_search_grounding
}
```

## LLM Interactions

The `gemini_generator.py` script contains several points of interaction with the Gemini Large Language Model:

1. **Model Availability Testing**
   - In the `get_available_model()` function, the script sends a minimal "Test" prompt to each model candidate
   - This confirms API connection and model availability before the main content generation
   - The script tries the requested model first, then falls back to a series of alternatives if needed

2. **Main Content Generation**
   - Primary LLM interaction occurs through the `content_agent.run_sync()` method in the `generate_content()` function
   - Inputs:
     - System prompt defining the agent as a "professional software engineer and technical documentation specialist"
     - Project context including name, organization, and project description prompt
     - Configurable parameters like temperature, tokens, etc.
   - Output is structured according to the `ProjectOutput` Pydantic model, including:
     - README content
     - Best practices
     - Recommended VS Code extensions
     - Documentation sources
     - Project type classification
     - Programming language identification

3. **Template Processing (When Using Existing Templates)**
   - The `template_agent` uses LLM to analyze and process GitHub templates
   - The agent can invoke local Python tools for analysis and placeholder replacement
   - Interactions include identifying variables in templates and making format decisions

4. **Google Search Grounding (For Gemini 2.x+ Models)**
   - When enabled, the module configures the Gemini model with a Google Search tool
   - The LLM can autonomously decide to search for current information about:
     - Framework versions
     - Best practices
     - Technical documentation
     - Development patterns
   - Search queries and sources are captured in the generation metadata

The entire process is managed through the Pydantic AI Agent framework, which handles the structured conversation with the LLM, ensuring outputs conform to the expected schemas and formats.

## Architecture Improvements

This module has been refactored from the original implementation to improve reliability and idempotency:

1. **Direct File Output:**
   - The Python script now writes both JSON and Markdown outputs directly to files
   - No more reliance on stdout/stdin for data exchange with Terraform

2. **Simplified Architecture:**
   - Replaced external data source with a more reliable null_resource approach
   - Eliminated intermediate JSON-to-Markdown conversion step
   - Single Python script handles all content generation and format conversion

3. **Better Error Handling:**
   - Robust error handling writes errors to both JSON and Markdown outputs
   - Includes detailed error messages and stack traces for easier debugging
   - Exit codes properly indicate success or failure

4. **Improved Idempotency:**
   - File-based approach ensures consistency across terraform runs
   - Local file data sources provide consistent interface for Terraform
   - Clear separation between generation and consumption of output files

5. **Configurable Token Parameters:**
   - Control temperature, top_p, top_k, and max_output_tokens through Terraform
   - Customize generation parameters based on project needs

These improvements make the module more maintainable, easier to debug, and more reliable in production environments.

## Implementation Details

The module uses a `null_resource` with a local-exec provisioner to invoke a Python script that:

1. Configures the Gemini API client with the provided API key
2. Sets up structured Pydantic models for the expected output format
3. Creates a Pydantic AI agent with the appropriate system prompts
4. Processes the project prompt to generate comprehensive documentation
5. Optionally converts values to placeholders for template reuse
6. Writes both JSON and Markdown output directly to files
7. Uses local_file data sources to read the outputs into Terraform

If template fetching from GitHub is requested, the script will:
1. Call the GitHub API to retrieve the template content
2. Process the template with the appropriate placeholders
3. Return the processed template with analysis information

## Requirements

- Python 3.8+ available in the execution environment
- Required Python packages (installed via `pip install -r requirements.txt`):
  - google-generativeai>=0.3.0
  - pydantic>=2.0.0  
  - pydantic-ai>=0.9.0
  - requests>=2.28.0

## Environment Variables

The module requires the GEMINI_API_KEY to be available. If using GitHub template fetching, an optional GITHUB_TOKEN can be provided for API authentication.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| project_prompt | The user's initial description of the project | `string` | n/a | yes |
| project_name | The name of the project/repository | `string` | n/a | yes |
| repo_org | The GitHub organization name | `string` | n/a | yes |
| gemini_api_key | The Gemini API key | `string` | n/a | yes |
| gemini_model | The Gemini model to use for generation | `string` | `"gemini-2.5-pro-preview-05-06"` | no |
| create_with_placeholders | Whether to create templates with placeholders | `bool` | `false` | no |
| template_instruction | Instructions for template formatting | `object` | `{}` | no |
| github_api_url | GitHub API URL for Enterprise support | `string` | `"https://api.github.com"` | no |
| push_to_github | Whether to push generated templates to GitHub | `bool` | `false` | no |
| github_token | GitHub token for authentication | `string` | `""` | no |
| target_repo | Target repository for pushing templates | `string` | `""` | no |
| target_path | Target path in the repository | `string` | `""` | no |
| target_branch | Target branch in the repository | `string` | `"main"` | no |

## Outputs

| Name | Description |
|------|-------------|
| generated_template_json | The generated template content in JSON format |
| generated_template_markdown | The generated template content in Markdown format |
| project_type | The detected project type |
| programming_language | The detected programming language |
| error_message | Error message, if any |
| stack_trace | Full Python stack trace for debugging when errors occur |
| used_search_grounding | Indicates if Google Search grounding was used |
