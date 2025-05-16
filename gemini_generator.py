#!/usr/bin/env python3
"""
Gemini content generation script for terraform-github-project
Retrieves AI-generated content using Gemini API based on project prompt and requirements

This script follows the Terraform external data source protocol:
- Reads JSON input from stdin
- Processes the input data using Gemini API
- Returns the result as JSON on stdout
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests  # For GitHub API requests

# Import required libraries
try:
    import google.generativeai as genai
    from pydantic import BaseModel, Field, ValidationError
    from pydantic_ai import Agent, RunContext, ModelRetry
    from pydantic_ai.models.gemini import GeminiModelSettings
except ImportError:
    missing = []
    try:
        import google.generativeai as genai
    except ImportError:
        missing.append("google-generativeai")
    
    try:
        from pydantic import BaseModel
    except ImportError:
        missing.append("pydantic")
        
    try:
        from pydantic_ai import Agent
    except ImportError:
        missing.append("pydantic-ai")
    
    print(json.dumps({"error": f"Required packages not installed: {', '.join(missing)}. Install with: pip install google-generativeai pydantic pydantic-ai"}))
    sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
GEMINI_MODEL = "gemini-1.5-pro-latest"  # Use the latest pro model

# Define Pydantic models for structured output
class ReadmeContent(BaseModel):
    """Model for README.md content"""
    title: str = Field(description="Project title")
    description: str = Field(description="Project description")
    overview: str = Field(description="Brief project overview")
    getting_started: str = Field(description="Getting started instructions")
    usage: str = Field(description="Usage examples")
    
class ProjectOutput(BaseModel):
    """Output model for project content generation"""
    readme_content: str = Field(description="Full README.md content")
    best_practices: list[str] = Field(description="List of 5-10 best practices")
    suggested_extensions: list[str] = Field(description="List of recommended VS Code extensions")
    documentation_source: list[str] = Field(description="List of helpful documentation sources")
    copilot_instructions: str = Field(description="Instructions for GitHub Copilot")
    project_type: str = Field(description="The type of project")
    programming_language: str = Field(description="The primary programming language")

class ProjectInfo(BaseModel):
    """Project context information for the agent"""
    project_name: str = Field(description="Name of the project")
    repo_org: str = Field(description="GitHub organization or username") 
    project_prompt: str = Field(description="Original project description")

# Gemini agent implementation
def create_gemini_agent():
    """Create a Gemini agent for project content generation"""
    # Define the agent with Gemini model and structured output type
    content_agent = Agent(
        'google-gla:gemini-1.5-pro-latest',
        deps_type=ProjectInfo,
        output_type=ProjectOutput,
        system_prompt=(
            "You are a professional software engineer and technical documentation specialist. "
            "Your task is to create comprehensive project documentation and guidance based on "
            "the project information provided. Focus on best practices, technical accuracy, and "
            "providing actionable guidance."
        ),
    )
    
    # Add system prompt function to provide project context
    @content_agent.system_prompt
    def add_project_context(ctx: RunContext[ProjectInfo]) -> str:
        """Add project context to the system prompt"""
        return f"""
        Project Name: {ctx.deps.project_name}
        Organization: {ctx.deps.repo_org}
        Description: {ctx.deps.project_prompt}
        
        You will analyze this project description to determine:
        - The project type (e.g., web application, CLI tool, API, library)
        - Primary programming language(s)
        - Appropriate best practices
        - Relevant tooling and extensions
        - Documentation needs
        
        Provide thorough, actionable documentation suitable for a professional software team.
        """
    
    return content_agent

# Define template fetch and processing agent
def create_template_agent():
    """Create a Gemini agent for template processing"""
    template_agent = Agent(
        'google-gla:gemini-1.5-flash-latest',  # Use a faster model for template processing
        deps_type=dict,  # Use dictionary for template context
        output_type=dict, # Return processed template
        system_prompt=(
            "You are a template processor specialized in working with software project templates. "
            "Your job is to process template files, replace placeholders, and ensure the templates "
            "are correctly formatted for the project context."
        )
    )
    
    @template_agent.tool
    def analyze_template(ctx: RunContext[dict], template_content: str) -> dict:
        """
        Analyze a template to identify placeholders and structure.
        
        Args:
            template_content: The template content to analyze
            
        Returns:
            A dictionary with template analysis
        """
        template_vars = []
        for var in ctx.deps.get('placeholder_vars', []):
            placeholder = ctx.deps.get('placeholder_format', '${%s}') % var
            if placeholder in template_content:
                template_vars.append(var)
                
        return {
            'identified_vars': template_vars,
            'has_placeholders': len(template_vars) > 0,
            'template_length': len(template_content)
        }
    
    @template_agent.tool
    def process_template(ctx: RunContext[dict], template_content: str, replacements: dict) -> str:
        """
        Process a template by replacing placeholders with values.
        
        Args:
            template_content: The template content
            replacements: Dictionary of replacements (placeholder -> value)
            
        Returns:
            Processed template content
        """
        result = template_content
        for placeholder, value in replacements.items():
            format_placeholder = ctx.deps.get('placeholder_format', '${%s}') % placeholder
            result = result.replace(format_placeholder, value)
        return result
    
    return template_agent

def configure_gemini_api():
    """Configure Gemini API with API key from environment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)


def fetch_github_template(repo: str, path: str, ref: str = "main", api_url_base: str = "https://api.github.com") -> str:
    """
    Fetch a template from GitHub repository.
    
    Args:
        repo: Repository name (e.g., 'owner/repo')
        path: Path to the template file
        ref: Git reference (branch, tag, commit)
        api_url_base: Base URL for the GitHub API (defaults to public GitHub API)
        
    Returns:
        The template content as string
    """
    import urllib.parse
    from base64 import b64decode
    
    try:
        # Handle special characters in path
        encoded_path = urllib.parse.quote(path, safe='')
        
        # Support both URL formats for GitHub API (with or without trailing slash)
        if api_url_base.endswith('/'):
            api_url = f"{api_url_base}repos/{repo}/contents/{encoded_path}"
        else:
            api_url = f"{api_url_base}/repos/{repo}/contents/{encoded_path}"
            
        # Add reference parameter if provided
        if ref:
            api_url = f"{api_url}?ref={ref}"
        
        # Set up headers with token if available
        headers = {
            "Accept": "application/vnd.github.v3+json"  # Explicitly request v3 API
        }
        
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"  # Using Bearer format for token
        
        logger.debug(f"Fetching template from API URL: {api_url}")
        
        # Make the request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        content_data = response.json()
        
        # Handle different response formats (file vs directory)
        if isinstance(content_data, list):
            raise ValueError(f"Path '{path}' refers to a directory, not a file")
            
        # GitHub API returns content as base64 encoded
        if "content" not in content_data:
            raise ValueError(f"No content found in the response for {path}")
            
        # Handle multi-line base64 content (GitHub wraps with newlines)
        raw_content = content_data["content"].replace('\n', '')
        content = b64decode(raw_content).decode("utf-8")
        return content
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching template from GitHub: {str(e)}")
        raise ValueError(f"Failed to fetch template from {repo}/{path}: {str(e)}")
    except ValueError as e:
        logger.error(f"Error processing GitHub response: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching template: {str(e)}")
        raise ValueError(f"Failed to fetch template from {repo}/{path}: {str(e)}")

def create_template_with_placeholders(content: str, placeholder_format: str, placeholder_vars: List[str]) -> str:
    """
    Convert concrete values to placeholders in generated content.
    
    Args:
        content: The content to process
        placeholder_format: Format string for placeholders (e.g. "____%s____")
        placeholder_vars: List of variable names for placeholders
        
    Returns:
        Content with placeholders
    """
    # Create a mapping of variable names and their placeholder replacements
    replacements = {
        var_name: placeholder_format % var_name 
        for var_name in placeholder_vars
    }
    
    # Replace all concrete values with their placeholders
    template_content = content
    for var_name, placeholder in replacements.items():
        if var_name == "project_name":
            template_content = template_content.replace(f"{var_name}", placeholder)
        elif var_name == "repo_org":
            template_content = template_content.replace(f"{var_name}", placeholder)
        elif var_name == "project_type":
            template_content = template_content.replace(f"{var_name}", placeholder)
        elif var_name == "programming_language":
            template_content = template_content.replace(f"{var_name}", placeholder)
            
    return template_content


def generate_content(project_prompt: str, repo_org: str, project_name: str, 
                    create_with_placeholders: bool = False,
                    placeholder_format: str = "${%s}",
                    placeholder_vars: List[str] = None) -> Dict[str, Any]:
    """
    Generate content using Gemini agent based on project prompt.
    
    Args:
        project_prompt: Description of the project
        repo_org: GitHub organization name
        project_name: Name of the project/repository
        create_with_placeholders: Whether to create content with placeholders
        placeholder_format: Format for placeholders
        placeholder_vars: Variables to convert to placeholders
        
    Returns:
        Dictionary containing generated content
    """
    if placeholder_vars is None:
        placeholder_vars = ["project_name", "repo_org", "project_type", "programming_language"]
    
    try:
        # Create project info for the agent
        project_info = ProjectInfo(
            project_name=project_name,
            repo_org=repo_org,
            project_prompt=project_prompt
        )
        
        # Create and configure the agent
        content_agent = create_gemini_agent()
        
        # Adjust model settings for more comprehensive output
        model_settings = GeminiModelSettings(
            temperature=0.2,  # Low temperature for more predictable output
            top_p=0.95,       # High top_p for diverse but relevant responses
            top_k=40,         # Standard top_k value
            max_output_tokens=8192,  # Allow longer outputs for comprehensive documentation
        )
        
        # Run the agent with the project info
        logger.info(f"Generating content for project '{project_name}'...")
        result = content_agent.run_sync(
            prompt="Generate comprehensive documentation and project setup guidance",
            deps=project_info,
            model_settings=model_settings
        )
        
        # Extract the structured output
        main_content = {
            "readme_content": result.output.readme_content,
            "best_practices": result.output.best_practices,
            "suggested_extensions": result.output.suggested_extensions,
            "documentation_source": result.output.documentation_source,
            "copilot_instructions": result.output.copilot_instructions
        }
        
        # Process content to add placeholders if requested
        if create_with_placeholders:
            for key in main_content:
                if isinstance(main_content[key], str):
                    main_content[key] = create_template_with_placeholders(
                        main_content[key], placeholder_format, placeholder_vars
                    )
        
        # Return the result as a dictionary
        return {
            "main": json.dumps(main_content),
            "project_type": result.output.project_type,
            "programming_language": result.output.programming_language
        }
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        # Return error information and fallback empty content
        return {
            "error": str(e),
            "main": json.dumps({}),
            "project_type": "Unknown",
            "programming_language": "Unknown"
        }


def main():
    """
    Main function that follows the Terraform external data source protocol:
    1. Read JSON from stdin
    2. Process the input
    3. Write JSON result to stdout
    """
    try:
        # Read input JSON from stdin
        input_json = sys.stdin.read()
        input_data = json.loads(input_json)
        
        # Extract parameters from input
        project_prompt = input_data.get('project_prompt')
        repo_org = input_data.get('repo_org')
        project_name = input_data.get('project_name')
        
        # Check for required parameters
        if not all([project_prompt, repo_org, project_name]):
            missing = []
            if not project_prompt: missing.append("project_prompt")
            if not repo_org: missing.append("repo_org")
            if not project_name: missing.append("project_name")
            error = f"Missing required parameters: {', '.join(missing)}"
            print(json.dumps({"error": error}))
            sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform
            
        # Get template generation settings
        # Convert string boolean to actual boolean
        create_with_placeholders_str = input_data.get('create_with_placeholders', "false")
        create_with_placeholders = create_with_placeholders_str.lower() == "true" if isinstance(create_with_placeholders_str, str) else bool(create_with_placeholders_str)
        
        # Parse the template_instruction JSON string if it exists
        template_instruction_str = input_data.get('template_instruction', "{}")
        try:
            template_instruction = json.loads(template_instruction_str) if isinstance(template_instruction_str, str) else template_instruction_str
        except json.JSONDecodeError:
            template_instruction = {}
            
        placeholder_format = template_instruction.get('placeholder_format', "${%s}")
        placeholder_vars = template_instruction.get('placeholder_variables', 
                                             ["project_name", "repo_org", "project_type", "programming_language"])
        
        # Check if we should use an existing template from GitHub
        use_existing_template = input_data.get('use_existing_template', False)
        result = {}
        
        # Configure API
        configure_gemini_api()
        
        if use_existing_template:
            # Get template fetching details
            template_repo = input_data.get('template_repo')
            template_path = input_data.get('template_path')
            template_ref = input_data.get('template_ref', 'main')
            
            # Support for GitHub Enterprise or other GitHub API endpoints
            github_api_url = input_data.get('github_api_url', 'https://api.github.com')
            
            if not all([template_repo, template_path]):
                print(json.dumps({"error": "Missing template repository or path"}))
                sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform
                
            logger.info(f"Fetching template from {template_repo}/{template_path} (ref: {template_ref})")
            try:
                # Fetch template from GitHub with configurable API URL
                template_content = fetch_github_template(
                    repo=template_repo, 
                    path=template_path, 
                    ref=template_ref,
                    api_url_base=github_api_url
                )
                
                # Process template with Gemini agent if needed
                if create_with_placeholders:
                    # Create template context
                    template_context = {
                        'placeholder_format': placeholder_format,
                        'placeholder_vars': placeholder_vars,
                        'project_name': project_name,
                        'repo_org': repo_org,
                        'project_prompt': project_prompt
                    }
                    
                    # Create and run template agent
                    template_agent = create_template_agent()
                    template_result = template_agent.run_sync(
                        prompt=f"Analyze and process template for {project_name}",
                        deps=template_context
                    )
                    
                    # Get template analysis
                    analysis = template_agent.run_sync(
                        prompt="Analyze the template structure",
                        deps=template_context,
                        tool_choice="analyze_template",
                        tool_params={"template_content": template_content}
                    )
                    
                    # Set result with the template content and analysis
                    project_type = "Unknown"
                    programming_language = "Unknown"
                    
                    # Try to extract project type and language from template
                    try:
                        template_data = json.loads(template_content)
                        project_type = template_data.get("project_type", "Unknown")
                        programming_language = template_data.get("programming_language", "Unknown")
                    except:
                        # Template might not be in JSON format
                        pass
                    
                    result = {
                        "main": template_content,
                        "project_type": project_type,
                        "programming_language": programming_language,
                        "template_analysis": json.dumps(analysis.output)
                    }
                else:
                    # Just return the raw template
                    result = {
                        "main": template_content,
                        "project_type": "Unknown", 
                        "programming_language": "Unknown"
                    }
            except Exception as e:
                logger.error(f"Error processing template: {str(e)}")
                # Fall back to generating content if template fetching fails
                result = generate_content(
                    project_prompt=project_prompt,
                    repo_org=repo_org,
                    project_name=project_name,
                    create_with_placeholders=create_with_placeholders,
                    placeholder_format=placeholder_format,
                    placeholder_vars=placeholder_vars
                )
        else:
            # Generate content with Gemini
            result = generate_content(
                project_prompt=project_prompt,
                repo_org=repo_org,
                project_name=project_name,
                create_with_placeholders=create_with_placeholders,
                placeholder_format=placeholder_format,
                placeholder_vars=placeholder_vars
            )
        
        # Return result as JSON to stdout
        print(json.dumps(result))
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
        sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform


if __name__ == "__main__":
    main()
