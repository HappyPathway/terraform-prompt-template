# Template Generator Module for Terraform GitHub Project

## Overview

This module provides an interface between Terraform and Google's Gemini API for generating project documentation and templates. It leverages the external data source to execute a Python script (`gemini_generator.py`) that uses Gemini's generative AI capabilities through a structured Pydantic AI agent implementation.

## Features

- Generate project documentation with Gemini AI
- Fetch existing templates from GitHub repositories
- Convert concrete values to placeholders for reusable templates
- Support for GitHub Enterprise through configurable API URLs
- Structured output format with error handling

## Usage

```hcl
module "template_generator" {
  source = "./modules/template_generator"

  # Required inputs
  project_prompt = "Create a web application for managing cloud infrastructure with React frontend and Go backend"
  project_name   = "cloud-manager"
  repo_org       = "my-organization"
  gemini_api_key = var.gemini_api_key  # Always use a variable for sensitive values

  # Optional: template formatting settings
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "${%s}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  
  # Optional: GitHub API URL for Enterprise environments
  github_api_url = "https://github.example.com/api/v3"
}

# Access generated template content
locals {
  template_content = module.template_generator.generated_template
  project_type     = module.template_generator.project_type
}
```

## Implementation Details

The module uses Terraform's external data source to invoke a Python script that:

1. Configures the Gemini API client with the provided API key
2. Sets up structured Pydantic models for the expected output format
3. Creates a Pydantic AI agent with the appropriate system prompts
4. Processes the project prompt to generate comprehensive documentation
5. Optionally converts values to placeholders for template reuse
6. Returns structured JSON output that Terraform can parse

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
| create_with_placeholders | Whether to create templates with placeholders | `bool` | `false` | no |
| template_instruction | Instructions for template formatting | `object` | `{}` | no |
| github_api_url | GitHub API URL for Enterprise support | `string` | `"https://api.github.com"` | no |

## Outputs

| Name | Description |
|------|-------------|
| generated_template | The generated template content |
| project_type | The detected project type |
| programming_language | The detected programming language |
| error_message | Error message, if any |
