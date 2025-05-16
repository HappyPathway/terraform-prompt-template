# Enterprise GitHub Template Example

This example demonstrates using the template_generator module with GitHub Enterprise and advanced placeholder handling. It shows how to:

1. Connect to a GitHub Enterprise instance
2. Generate content with Gemini
3. Use custom placeholder formats
4. Save generated templates back to GitHub Enterprise

## Usage

1. Create a `terraform.tfvars` file with your API keys and GitHub Enterprise URL:

```
gemini_api_key      = "YOUR_API_KEY"
github_token        = "YOUR_GITHUB_ENTERPRISE_TOKEN"
github_enterprise_url = "https://github.example.com/api/v3"
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
module "enterprise_template_example" {
  source          = "../../.."  # Path to the root module
  
  # Required inputs
  project_prompt  = "Create a microservice architecture for an e-commerce application"
  project_name    = "ecommerce-platform" 
  repo_org        = "my-enterprise"
  gemini_api_key  = var.gemini_api_key
  
  # GitHub Enterprise configuration
  github_api_url  = var.github_enterprise_url
  
  # Template generation settings
  generate_prompts = true
  
  # Template saving settings
  save_generated_template = true
  template_save_repo      = "my-enterprise/templates"
  template_save_path      = "microservices/ecommerce-template.json"
  template_save_branch    = "main"
  template_commit_author  = "Template Generator"
  template_commit_email   = "template-generator@example.com"
  
  # Required root module settings
  base_repository = {
    name        = "ecommerce-platform" 
    description = "Microservice architecture for e-commerce application"
    visibility  = "private"
  }
  
  repositories = [
    {
      name        = "ecommerce-api-gateway",
      description = "API Gateway service for the e-commerce platform"
    },
    {
      name        = "ecommerce-product-service",
      description = "Product management microservice"
    }
  ]
}
```

> **Note:** Before running Terraform, set the GitHub token as an environment variable:  
> `export GITHUB_TOKEN=your_github_token_here`

## Custom Placeholder Format

This example uses a custom placeholder format `___%s___` which creates placeholders like:

```
# ___project_name___

A project by ___author___ (___email___)
Created on ___date___

## Overview
This ___project_type___ project uses ___programming_language___ to implement...
```

## GitHub Enterprise Integration

The module works with GitHub Enterprise by:

1. Using the specified GitHub Enterprise API URL for API calls
2. Using the provided GitHub token for authentication
3. Saving the generated template back to the GitHub Enterprise repository
4. Using the specified author and email for commit information

## Expected Output

The module will:

1. Connect to your GitHub Enterprise instance
2. Generate project content based on the provided prompt using Gemini
3. Format the content with custom placeholders
4. Save the template back to your GitHub Enterprise repository
5. Return the generated template and project information

## Notes

- This example requires a valid GitHub Enterprise token with appropriate permissions
- The GitHub Enterprise URL should point to the API endpoint
- Custom placeholder variables like `author`, `email`, and `date` can be added
