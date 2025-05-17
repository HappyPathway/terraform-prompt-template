# FastAPI Python Application Example

/**
 * FastAPI Application Template Example
 * 
 * This example demonstrates using the template_generator module
 * to create a comprehensive FastAPI application in Python.
 */


# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "fastapi_template_generator" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = file("${path.module}/fastapi-project-plan.md")
  project_name    = "fastapi-ecommerce-api" 
  gemini_model    = "google-gla:gemini-1.5-pro"  # Using 1.5 Pro as it's more reliable
  repo_org        = "HappyPathway"
  gemini_api_key  = var.gemini_api_key
  create_with_placeholders = true
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  github_api_url   = "https://api.github.com"  # Optional, default is GitHub API
  
  # GitHub push configuration
  push_to_github  = true
  github_token    = var.github_token
  target_repo     = var.target_repo
  target_path     = "fastapi-template.json"
  target_branch   = var.target_branch
}

# Output the results
output "fastapi_template_generator" {
  description = "Generated FastAPI project template"
  value       = module.fastapi_template_generator
}
