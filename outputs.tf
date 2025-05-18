# output "copilot_instructions" {
#   description = "The GitHub Copilot instructions in Markdown format"
#   value       = file(local.copilot_instructions_path)
#   depends_on = [null_resource.generate_content]
# }

# output "github_project_prompt" {
#   description = "The GitHub project prompt content in Markdown format for .github/prompts directory"
#   value       = file(local.github_project_prompt_path)
#   depends_on = [null_resource.generate_content]
# }

