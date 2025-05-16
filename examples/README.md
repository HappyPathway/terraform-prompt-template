# Template Generator Module Examples

This directory contains examples demonstrating how to use the template generator module in various scenarios.

## Available Examples

### 1. [Basic Example](basic/)

The simplest usage of the template generator module to generate project documentation using Gemini API without any advanced options.

```hcl
module "basic_template" {
  source        = "../../" 
  project_prompt = "Create a web application for customer relationship management..."
  project_name   = "crm-webapp" 
  repo_org       = "example-org"
  gemini_api_key = var.gemini_api_key
}
```

### 2. [GitHub Template Example](github-template/)

This example demonstrates fetching an existing template from a GitHub repository and processing it with the template generator module.

```hcl
module "github_template" {
  source = "../../"
  
  # Core settings
  project_prompt = "Create a web application for customer relationship management..."
  project_name   = "crm-webapp" 
  repo_org       = "example-org"
  gemini_api_key = var.gemini_api_key

  # GitHub template fetching
  use_existing_template = true
  template_repo         = "example-org/project-templates"
  template_path         = "templates/webapp-template.json"
  template_ref          = "main"
}
```

### 3. [Enterprise Example](enterprise/)

A more complex example showing GitHub Enterprise integration with advanced placeholder handling and template saving.

```hcl
module "enterprise_template" {
  source = "../../"
  
  # Core settings
  project_prompt = "Create a microservice architecture for an e-commerce application..."
  project_name   = "ecommerce-platform" 
  repo_org       = "my-enterprise"
  gemini_api_key = var.gemini_api_key

  # GitHub Enterprise configuration
  github_api_url = var.github_enterprise_url

  # Advanced placeholder handling
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "___%s___"
    placeholder_variables = ["project_name", "repo_org", "project_type", ...]
  }
  
  # Save generated template
  save_generated_template = true
  template_save_repo      = "my-enterprise/templates"
  template_save_path      = "microservices/ecommerce-template.json"
}
```

## Running the Examples

Each example directory contains:

1. `main.tf` - The Terraform configuration file
2. `README.md` - Detailed documentation for the specific example

To use any example:

1. Navigate to the example directory
2. Create a `terraform.tfvars` file with required variables
3. Run `terraform init` and `terraform apply`

## Notes

- These examples require access to the Gemini API
- Some examples may require GitHub or GitHub Enterprise access tokens
- The examples use relative paths (`../../`) to reference the module
