/**
 * Fixed GitHub Template Example
 * 
 * This example demonstrates using the template_generator module
 * to fetch an existing template from GitHub and process it.
 */

# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "template_generator_example" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name    = "crm-webapp" 
  project_type    = "react-webapp"  # Specify the project type
  gemini_model    = "google-gla:gemini-2.5-pro-preview-05-06"  # Using latest 2.5 Pro model
  repo_org        = "HappyPathway"
  gemini_api_key  = var.gemini_api_key
  create_with_placeholders = true
  enable_search_grounding = false  # Disable search grounding for this example
  template_dir = "${path.root}/templates"
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  github_api_url   = "https://api.github.com"  # Optional, default is GitHub API
  
  # GitHub push configuration
  push_to_github  = false
  github_token    = var.github_token
  target_repo     = var.target_repo
  target_path     = var.target_path
  target_branch   = var.target_branch
}

# Output the results
output "template_generator" {
  description = "All generated repositories"
  value       = module.template_generator_example.generated_template_markdown
}

resource local_file "generated_template" {
  filename = "${path.root}/templates/react-webapp.md"
  content  = module.template_generator_example.generated_template_markdown
}