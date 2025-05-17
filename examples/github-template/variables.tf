
variable "gemini_api_key" {
  description = "API key for Gemini API"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token for API authentication"
  type        = string
  sensitive   = true
  default     = ""
}

variable "target_repo" {
  description = "Target repository for writing the template"
  type        = string
  default     = "PromptTemplates"
}

variable "target_branch" {
  description = "Branch to write to in the target repo"
  type        = string
  default     = "main"
}

variable "target_path" {
  description = "Path in the repo where to save the template"
  type        = string
  default     = "crm-template"
}

