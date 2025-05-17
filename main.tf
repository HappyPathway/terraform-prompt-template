# Template Generator Module
# This module handles template generation using Gemini API

# Define local variables for file paths
locals {
  # Local file paths for the generated output files
  json_output_path = "${var.template_dir}/${var.project_type}-template.json"
  markdown_output_path = "${var.template_dir}/${var.project_type}-template.md"
}

# Use null_resource with local-exec provisioner to run the Python script
resource "null_resource" "generate_content" {
  # This will ensure the script runs every time due to the uuid()
  # If idempotency is needed, remove the run_id from the triggers
  triggers = {
    project_prompt = var.project_prompt
    project_name = var.project_name
    repo_org = var.repo_org
    create_with_placeholders = var.create_with_placeholders
    enable_search_grounding = var.enable_search_grounding
    gemini_model = var.gemini_model
    temperature = var.model_settings.temperature
    top_p = var.model_settings.top_p
    top_k = var.model_settings.top_k
    max_output_tokens = var.model_settings.max_output_tokens
    disable_cache = var.disable_cache
    cache_version = var.cache_version
  }

  # Run the Python script with command line arguments
  provisioner "local-exec" {
    command = <<-EOT
      python ${path.module}/gemini_generator.py \
        --project_prompt "${var.project_prompt}" \
        --repo_org "${var.repo_org}" \
        --project_name "${var.project_name}" \
        --gemini_model "${var.gemini_model}" \
        --json_output "${local.json_output_path}" \
        --markdown_output "${local.markdown_output_path}" \
        --create_with_placeholders "${var.create_with_placeholders}" \
        --enable_search_grounding "${var.enable_search_grounding}" \
        --placeholder_format "${var.template_instruction.placeholder_format}" \
        --placeholder_vars "${join(",", var.template_instruction.placeholder_variables)}" \
        --temperature ${var.model_settings.temperature} \
        --top_p ${var.model_settings.top_p} \
        --top_k ${var.model_settings.top_k} \
        --max_output_tokens ${var.model_settings.max_output_tokens}
    EOT
    
    environment = {
      GITHUB_TOKEN = var.github_token,
      GEMINI_API_KEY= var.gemini_api_key
    }
  }
}

# Use local_file data source to read the generated JSON file
data "local_file" "generated_json" {
  depends_on = [null_resource.generate_content]
  filename = local.json_output_path
}

# Use local_file data source to read the generated Markdown file
data "local_file" "generated_markdown" {
  depends_on = [null_resource.generate_content]
  filename = local.markdown_output_path
}

# Parse the JSON content to extract project details
locals {
  # Parse the JSON content safely
  parsed_json = try(jsondecode(data.local_file.generated_json.content), {})
  
  # Extract key information
  project_type = try(local.parsed_json.project_type, "Unknown")
  programming_language = try(local.parsed_json.programming_language, "Unknown")
  
  # Handle errors gracefully
  has_error = contains(keys(local.parsed_json), "error")
  has_stack_trace = contains(keys(local.parsed_json), "stack_trace")
  error_message = local.has_error ? local.parsed_json.error : null
  stack_trace = local.has_stack_trace ? local.parsed_json.stack_trace : null
}

# Parse the target_repo into owner and repository name
locals {
  repo_parts = var.push_to_github && var.target_repo != "" ? split("/", var.target_repo) : ["", ""]
  owner      = length(local.repo_parts) == 2 ? local.repo_parts[0] : ""
  repository = length(local.repo_parts) == 2 ? local.repo_parts[1] : ""
}

# Push the JSON template to the specified GitHub repository using the GitHub provider
resource "github_repository_file" "json_template_file" {
  count               = var.push_to_github ? 1 : 0
  repository          = var.target_repo
  branch              = var.target_branch
  file                = "${dirname(var.target_path)}/${basename(var.target_path)}.json"
  content             = data.local_file.generated_json.content
  commit_message      = "Update generated JSON template for ${local.project_type} project"
  commit_author       = "Terraform Template Generator"
  commit_email        = "terraform@example.com"
  overwrite_on_create = true
}

# Push the Markdown template to the specified GitHub repository using the GitHub provider
resource "github_repository_file" "markdown_template_file" {
  count               = var.push_to_github ? 1 : 0
  repository          = var.target_repo
  branch              = var.target_branch
  file                = "${dirname(var.target_path)}/${basename(var.target_path)}.md"
  content             = data.local_file.generated_markdown.content
  commit_message      = "Update generated Markdown template for ${local.project_type} project"
  commit_author       = "Terraform Template Generator"
  commit_email        = "terraform@example.com"
  overwrite_on_create = true
}
