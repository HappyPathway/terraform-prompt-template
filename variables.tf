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
  default     = true
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

variable "enable_search_grounding" {
  description = "Whether to enable Google Search grounding for Gemini 2.x+ models"
  type        = bool
  default     = true
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

variable "model_settings" {
  description = "Configuration settings for the Gemini model"
  type = object({
    temperature        = optional(number, 0.2)
    top_p              = optional(number, 0.95)
    top_k              = optional(number, 40)
    max_output_tokens  = optional(number, 32768)
    candidate_count    = optional(number, 1)
  })
  default = {}
}

# GitHub push configuration variables
variable "github_token" {
  description = "GitHub personal access token for API authentication"
  type        = string
  sensitive   = true
  default     = ""
}

variable "target_path" {
  description = "Path in the repo where to save the template"
  type        = string
  default     = "template.json"
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

variable github_prompts_dir {
  description = "Directory to store GitHub prompts files (.github/prompts)"
  type        = string
  default     = ".github/prompts"
}