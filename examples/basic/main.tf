/**
 * Basic Template Generator Example
 * 
 * This example demonstrates the simplest usage of the template_generator module
 * to generate project documentation using Gemini API without any advanced options.
 */

variable "gemini_api_key" {
  description = "API key for Gemini API"
  type        = string
  sensitive   = true
}

module "basic_template" {
  source = "../../"  # Relative path to the module

  # Required inputs
  project_prompt = "Create a web application for customer relationship management with a React frontend and Node.js backend"
  project_name   = "crm-webapp" 
  repo_org       = "example-org"
  gemini_api_key = var.gemini_api_key
  
  # Enable search grounding for research-based expansion of the project description
  enable_search_grounding = true
  
  # Configure model parameters to ensure sufficient output tokens for comprehensive research
  model_settings = {
    temperature       = 0.2
    max_output_tokens = 32768  # Maximum tokens for thorough research
  }
}

# Output the results
output "generated_content" {
  description = "Generated template content"
  value       = module.basic_template.generated_template
  sensitive   = true  # Mark as sensitive to prevent API output from showing in logs
}

output "project_type" {
  description = "Detected project type"
  value       = module.basic_template.project_type
}

output "programming_language" {
  description = "Detected programming language"
  value       = module.basic_template.programming_language
}
