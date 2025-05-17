output "generated_template_json" {
  description = "The generated template content in JSON format"
  value       = data.local_file.generated_json.content
}

output "generated_template_markdown" {
  description = "The generated template content in Markdown format"
  value       = data.local_file.generated_markdown.content
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

output "stack_trace" {
  description = "Stack trace for debugging if an error occurred"
  value       = local.stack_trace
}

output "used_search_grounding" {
  description = "Whether search grounding was used for this generation"
  value       = try(local.parsed_json.used_search_grounding, false)
}
