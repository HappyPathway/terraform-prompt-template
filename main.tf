# Template Generator Module
# This module handles template generation using Gemini API

# Define local variables for file paths
locals {
  # Local file paths for the generated output files
  json_output_path = "${var.template_dir}/${var.project_type}-template.json"
  markdown_output_path = "${var.template_dir}/${var.project_type}-template.md"
  project_prompt_path = "${path.module}/project-prompt.md"
  copilot_instructions_path = "${path.module}/copilot-instructions.md"
  
  # GitHub-specific paths
  github_project_prompt_path = "${var.github_prompts_dir}/project-prompt.md"
}

locals {
  command = <<-EOT
   python ${path.module}/gemini_generator.py \
        --project_prompt "${var.project_prompt}" \
        --repo_org "${var.repo_org}" \
        --project_name "${var.project_name}" \
        --gemini_model "${var.gemini_model}" \
        --json_output "${local.json_output_path}" \
        --markdown_output "${local.markdown_output_path}" \
        --project_prompt_output "${local.project_prompt_path}" \
        --copilot_instructions_output "${local.copilot_instructions_path}" \
        --github_project_prompt_output "${local.github_project_prompt_path}" \
        --enable_search_grounding "${var.enable_search_grounding}" \
        --placeholder_format "${var.template_instruction.placeholder_format}" \
        --placeholder_vars "${join(",", var.template_instruction.placeholder_variables)}" \
        --temperature ${var.model_settings.temperature} \
        --top_p ${var.model_settings.top_p} \
        --top_k ${var.model_settings.top_k} \
        --max_output_tokens ${var.model_settings.max_output_tokens}
  EOT
}

resource local_file "command" {
  # This is a workaround to ensure the command is executed
  # The actual execution happens in the null_resource
  filename = "${path.root}/command.sh"
  content  = local.command
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
  }

  # Run the Python script with command line arguments
  provisioner "local-exec" {
    command = local.command
    environment = {
      GITHUB_TOKEN = var.github_token,
      GEMINI_API_KEY= var.gemini_api_key
    }
  }
}
