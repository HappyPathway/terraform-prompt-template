terraform {
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = ">= 2.0.0"
    }
    github = {
      source  = "integrations/github"
      version = ">= 5.0.0"
    }
  }
  required_version = ">= 1.0.0"
}
