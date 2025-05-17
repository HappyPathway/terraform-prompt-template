# Template Generator Module
# This module handles template generation using Gemini API

# Use external data source to run the Python script and get the output
data "external" "gemini_content" {
  # Use the fixed script that follows the Terraform external data source protocol
  program = ["bash", "-c", "export GEMINI_API_KEY='${var.gemini_api_key}' && python ${path.module}/gemini_generator.py"]

  # Pass the data as query parameter according to external data source protocol
  query = {
    project_prompt          = var.project_prompt
    project_name            = var.project_name
    repo_org                = var.repo_org
    create_with_placeholders = tostring(var.create_with_placeholders)
    template_instruction    = jsonencode(var.template_instruction)
    github_api_url          = var.github_api_url
    template_model          = var.gemini_model
  }
}

locals {
  # Handle potential errors in the response
  has_error = contains(keys(data.external.gemini_content.result), "error")

  # Parse the responses
  generated_template = local.has_error ? "{\"error\": \"${data.external.gemini_content.result.error}\"}" : data.external.gemini_content.result.main
  
  # Extract project type and language from response
  project_type = try(data.external.gemini_content.result.project_type, "Unknown")
  programming_language = try(data.external.gemini_content.result.programming_language, "Unknown")
  
  # Extract any error message for output
  error_message = local.has_error ? data.external.gemini_content.result.error : null
  
  # Local file path for the template
  template_file_path = "${path.module}/generated_template.json"
}

# Create a local file with the generated template for debugging (always created)
resource "local_file" "generated_template" {
  content  = local.generated_template
  filename = local.template_file_path
}

# Parse the target_repo into owner and repository name
locals {
  repo_parts = var.push_to_github && var.target_repo != "" ? split("/", var.target_repo) : ["", ""]
  owner      = length(local.repo_parts) == 2 ? local.repo_parts[0] : ""
  repository = length(local.repo_parts) == 2 ? local.repo_parts[1] : ""
}

# Push the template to the specified GitHub repository using the GitHub provider
provider "github" {
  token = var.push_to_github ? var.github_token : null
  owner = local.owner
}

resource "github_repository_file" "template_file" {
  count               = var.push_to_github ? 1 : 0
  repository          = local.repository
  branch              = var.target_branch
  file                = var.target_path
  content             = local.generated_template
  commit_message      = "Update generated template for ${local.project_type} project"
  commit_author       = "Terraform Template Generator"
  commit_email        = "terraform@example.com"
  overwrite_on_create = true
}
