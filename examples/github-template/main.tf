/**
 * Fixed GitHub Template Example
 * 
 * This example demonstrates using the template_generator module
 * to fetch an existing template from GitHub and process it.
 */

# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "smart_invest_template_generator" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = <<EOT
    Create a Python based app for analyzing trade and investment data.
    It should able to output PDF reports and email them to subscribers.
    It should be able to run in Github Actions as a cron job and should fetch data from
    publicly available APIs and databases. It should use Pydantic and PydanticAI to 
    query Gemini and Google Search for data and information. 
    It should able to predict patterns. Track history of investment predictions and grade itself.
    Part of the daily report should include it's previous prediction and rating on accuracy.
    We will need to use multiple models and agents working in concert to achieve this.
    We will want to leverage SQLAlchemy and SQLite to store the data, we will want to 
    push and pull this data from GCS.
EOT
  project_name    = "smart-invest"
  project_type    = "python-github-actions"  # Specify the project type
  gemini_model    = "gemini-2.5-pro-preview-05-06"  # Using latest 2.5 Pro model
  repo_org        = "HappyPathway"
  gemini_api_key  = var.gemini_api_key
  create_with_placeholders = true
  # Enable search grounding for all prompts - ensures Gemini can research and expand project details
  # This allows minimal prompts to be expanded by the model rather than relying on hardcoded content
  enable_search_grounding = true
  template_dir = "${path.root}/templates"
  template_instruction = {
    placeholder_format    = "{{%s}}"
    placeholder_variables = ["project_name", "repo_org", "project_type", "programming_language"]
    generate_example      = true
  }
  # Configure model parameters to ensure sufficient output tokens for comprehensive research
  model_settings = {
    temperature        = 0.2        # Lower temperature for more predictable output
    top_p              = 0.95       # Diverse but relevant responses
    top_k              = 40         # Standard top_k value
    max_output_tokens  = 32768      # Maximum tokens for thorough research-based outputs
    candidate_count    = 1
  }
  target_path     = var.target_path
}

# output "copilot_instructions" {
#   description = "Generated template from GitHub"
#   value       = module.smart_invest_template_generator.copilot_instructions
# }

# output "github_project_prompt" {
#   description = "Generated GitHub project prompt"
#   value       = module.smart_invest_template_generator.github_project_prompt
# }