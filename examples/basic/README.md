# Basic Template Generator Example

This example demonstrates the simplest usage of the template_generator module to generate project documentation using Gemini API without any advanced options.

## Usage

1. Create a `terraform.tfvars` file with your API key:

```
gemini_api_key = "YOUR_API_KEY"
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
module "basic_template" {
  source = "../../"  # Relative path to the module

  # Required inputs
  project_prompt = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name   = "crm-webapp" 
  repo_org       = "example-org"
  gemini_api_key = var.gemini_api_key
}

# Output the results
output "generated_content" {
  description = "Generated template content"
  value       = module.basic_template.generated_template
  sensitive   = true  # Mark as sensitive to prevent API output from showing in logs
}
```

## Expected Output

The module will generate project documentation based on the provided prompt, including:

- README content
- Best practices
- Suggested VS Code extensions
- GitHub Copilot instructions
- Project type and programming language detection

## Notes

- This example uses the Gemini model to generate content from scratch
- No template fetching or placeholder handling is used in this example
- For more advanced usage, see the other examples in this directory
