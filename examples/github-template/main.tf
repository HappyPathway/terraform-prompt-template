/**
 * Fixed GitHub Template Example
 * 
 * This example demonstrates using the template_generator module
 * to fetch an existing template from GitHub and process it.
 */

variable "gemini_api_key" {
  description = "API key for Gemini API"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token for API authentication"
  type        = string
  sensitive   = true
  default     = ""  # Optional, as public repos don't require authentication
}

# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "template_generator_example" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name    = "crm-webapp" 
  repo_org        = "HappyPathway"
  gemini_api_key  = var.gemini_api_key
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  github_api_url   = "https://api.github.com"  # Optional, default is GitHub API
}

# Output the results
output "template_generator_example" {
  description = "All generated repositories"
  value       = module.template_generator_example
}
