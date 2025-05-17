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
  default     = "gemini-2.5-pro-preview-05-06"  # Default to latest 2.5 Pro preview as of May 2025
}

# GitHub push configuration variables
variable "github_token" {
  description = "GitHub personal access token for API authentication"
  type        = string
  sensitive   = true
  default     = ""
}

variable "push_to_github" {
  description = "Whether to push the generated template to a GitHub repository"
  type        = bool
  default     = false
}

variable "target_repo" {
  description = "Target repository for writing the template"
  type        = string
  default     = "HappyPathway/PromptTemplates"
}

variable "target_path" {
  description = "Path in the repo where to save the template"
  type        = string
  default     = "template.json"
}

variable "target_branch" {
  description = "Branch to write to in the target repo"
  type        = string
  default     = "main"
}

variable project_type {
  description = "The type of project (e.g., web, mobile, etc.)"
  type        = string
  default     = "web"
}

variable template_dir {
  description = "Directory to store the generated template files"
  type        = string
  default     = ""
}