/**
 * Fixed Enterprise GitHub Template Example
 * 
 * This example demonstrates using the template_generator module
 * with GitHub Enterprise and advanced placeholder handling.
 */

variable "gemini_api_key" {
  description = "API key for Gemini API"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub Enterprise personal access token"
  type        = string
  sensitive   = true
}

variable "github_enterprise_url" {
  description = "GitHub Enterprise API URL"
  type        = string
  default     = "https://github.example.com/api/v3"
}

# The GitHub token should be set as an environment variable before running Terraform
# In a shell: export GITHUB_TOKEN=your_token_here
# This is more reliable than using local-exec which only affects the current command

module "enterprise_template_example" {
  source          = "../.."  # Path to the root module, not the submodule
  
  # Required inputs
  project_prompt  = "Create a microservice architecture for an e-commerce application with service discovery, API gateway, and event-driven design"
  project_name    = "ecommerce-platform" 
  repo_org        = "my-enterprise"
  gemini_api_key  = var.gemini_api_key
  
  # GitHub Enterprise configuration
  github_api_url  = var.github_enterprise_url
  
  # Generate content with Gemini
  generate_prompts = true
  
  # Template saving settings
  save_generated_template = true
  template_save_repo      = "my-enterprise/templates"
  template_save_path      = "microservices/ecommerce-template.json"
  template_save_branch    = "main"
  template_commit_author  = "Template Generator"
  template_commit_email   = "template-generator@example.com"
  
  # Other required settings for the root module to work
  base_repository = {
    name        = "ecommerce-platform" 
    description = "Microservice architecture for e-commerce application"
    visibility  = "private"
  }
  
  repositories = [
    {
      name        = "ecommerce-api-gateway"
      description = "API Gateway service for the e-commerce platform"
    },
    {
      name        = "ecommerce-product-service" 
      description = "Product management microservice"
    },
    {
      name        = "ecommerce-order-service"
      description = "Order processing microservice"
    }
  ]
}

# Output the results
output "all_repos" {
  description = "All generated repositories"
  value       = module.enterprise_template_example.all_repos
}
