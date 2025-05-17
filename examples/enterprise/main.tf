/**
 * Fixed Enterprise GitHub Template Example
 * 
 * This example demonstrates using the template_generator module
 * with GitHub Enterprise and advanced placeholder handling.
 */

variable "gemini_api_key" {
  description = "API key for Gemini API"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub Enterprise personal access token"
  type        = string
  sensitive   = true
}

variable "github_enterprise_url" {
  description = "GitHub Enterprise API URL"
  type        = string
  default     = "https://github.example.com/api/v3"
}

# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "enterprise_template_example" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = "Create a microservice architecture for an e-commerce application with service discovery, API gateway, and event-driven design"
  project_name    = "ecommerce-platform" 
  repo_org        = "my-enterprise"
  gemini_model    = "google-gla:gemini-2.5-pro-preview-05-06"  # Using latest 2.5 Pro model
  gemini_api_key  = var.gemini_api_key
  
  # GitHub Enterprise configuration
  github_api_url  = var.github_enterprise_url
  
  # Template formatting settings
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  
  # GitHub push configuration
  push_to_github  = true
  github_token    = var.github_token
  target_repo     = "my-enterprise/templates"
  target_path     = "microservices/ecommerce-template.json"
  target_branch   = "main"
  template_dir    = "${path.root}/templates"
}

# Output the results
output "enterprise_template_example" {
  description = "Generated enterprise template"
  value       = module.enterprise_template_example
}
