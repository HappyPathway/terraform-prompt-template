# GitHub Template Example

This example demonstrates fetching an existing template from a GitHub repository and processing it using the template_generator module.

## Usage

1. Create a `terraform.tfvars` file with your API keys:

```
gemini_api_key = "YOUR_API_KEY"
github_token   = "YOUR_GITHUB_TOKEN"  # Optional for public repos
```

2. Initialize Terraform:

```
terraform init
```

3. Run Terraform:

```
terraform apply
```

## Example Terraform Configuration

```hcl
# Important: This example uses the root module, not the template_generator submodule directly
module "template_generator_example" {
  source          = "../../.."  # Path to the root module
  
  # Required inputs
  project_prompt  = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name    = "crm-webapp" 
  repo_org        = "example-org"
  gemini_api_key  = var.gemini_api_key
  
  # GitHub template settings 
  use_existing_template = true
  template_repo         = "example-org/project-templates"
  template_path         = "templates/webapp-template.json"
  template_ref          = "main"  # Branch, tag, or commit hash
  
  # Template generation settings
  generate_prompts = true
  
  # Required root module settings
  base_repository = {
    name        = "crm-webapp" 
    description = "Customer relationship management web application"
    visibility  = "private"
  }
  
  repositories = []  # No additional repositories in this example
}
```

> **Note:** Before running Terraform, set the GitHub token as an environment variable:  
> `export GITHUB_TOKEN=your_github_token_here`

## Template Format

The expected template format in GitHub repository is a JSON file that contains project documentation sections:

```json
{
  "readme_content": "# {{project_name}}\n\nDescription of the project...",
  "best_practices": [
    "Practice 1",
    "Practice 2",
    "Practice 3"
  ],
  "suggested_extensions": [
    "github.copilot",
    "github.copilot-chat",
    "ms-vscode.vscode-typescript-next"
  ],
  "documentation_source": [
    "https://example.com/docs"
  ],
  "copilot_instructions": "# GitHub Copilot Instructions\n\nCustom instructions for Copilot...",
  "project_type": "{{project_type}}",
  "programming_language": "{{programming_language}}"
}
```

## Expected Output

The module will:

1. Fetch the template from the specified GitHub repository
2. Replace placeholders with actual values if requested
3. Return the processed template content
4. Detect project type and programming language from the template

## Notes

- If the template cannot be fetched, the module will fall back to generating content
- The GitHub token is optional for public repositories
- You can customize the placeholder format to match your existing templates
