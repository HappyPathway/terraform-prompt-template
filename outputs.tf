output "generated_template" {
  description = "The generated template content"
  value       = local.generated_template
}

output "project_type" {
  description = "The detected project type from the prompt"
  value       = local.project_type
}

output "programming_language" {
  description = "The detected programming language from the prompt"
  value       = local.programming_language
}

output "error_message" {
  description = "Error message, if any"
  value       = local.error_message
}
