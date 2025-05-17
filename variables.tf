variable "project_prompt" {
  description = "The user's initial description of what they're trying to build"
  type        = string
}

variable "repo_org" {
  description = "The GitHub organization name"
  type        = string
}

variable "project_name" {
  description = "The name of the project/repository"
  type        = string
}

variable "gemini_api_key" {
  description = "The Gemini API key for authentication"
  type        = string
  sensitive   = true
}

variable "create_with_placeholders" {
  description = "Whether to create templates with placeholders instead of actual values"
  type        = bool
  default     = false
}

variable "template_instruction" {
  description = "Instructions for template formatting"
  type = object({
    placeholder_format    = optional(string, "{{%s}}")
    placeholder_variables = optional(list(string), ["project_name", "repo_org", "project_type", "programming_language"])
    generate_example      = optional(bool, false)
  })
  default = {}
}

variable "github_api_url" {
  description = "GitHub API URL for template fetching (for GitHub Enterprise support)"
  type        = string
  default     = "https://api.github.com"
}

variable gemini_model {
  description = "The model to use for the Gemini API"
  type        = string
  default     = "gemini-2.0-pro"  # Default model
}