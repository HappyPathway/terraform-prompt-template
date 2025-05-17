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
import traceback
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests  # For GitHub API requests

# Import required libraries
try:
    import google.generativeai as genai
    from pydantic import BaseModel, Field, ValidationError
    from pydantic_ai import Agent, RunContext, ModelRetry
    from pydantic_ai.models.gemini import GeminiModelSettings
    from google.genai.types import Tool, GoogleSearch
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

# Constants for feature flags
ENABLE_SEARCH_GROUNDING = True  # Set to False to disable Google Search grounding

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

# Helper function to get available models and select the best one
def get_available_model(requested_model: str = 'gemini-1.5-pro'):
    """Get an available model based on the requested one or fall back to a suitable default."""
    
    # Clean up model name (remove any google-gla: prefix)
    if requested_model.startswith('google-gla:'):
        requested_model = requested_model.split(':', 1)[1]
    
    # Remove any 'models/' prefix
    if requested_model.startswith('models/'):
        requested_model = requested_model[7:]
    
    # Try the requested model directly
    try:
        logger.info(f"Trying requested model: {requested_model}")
        model = genai.GenerativeModel(requested_model)
        response = model.generate_content("Test")
        logger.info(f"Successfully using requested model: {requested_model}")
        return requested_model
    except Exception as e:
        logger.warning(f"Requested model {requested_model} not available: {str(e)}")
    
    # Try modern models by priority (newest first, based on May 2025 availability)
    candidate_models = [
        # Gemini 2.5 models (newest)
        "gemini-2.5-pro-preview-05-06",  # Latest 2.5 Pro preview as of May 2025
        "gemini-2.5-flash-preview-04-17", # Latest 2.5 Flash preview
        # Gemini 2.0 models
        "gemini-2.0-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite", # Cost-efficient version
        # Gemini 1.5 models (still very capable)
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b", # Smaller, faster model
        # Legacy models (fallbacks)
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    for candidate in candidate_models:
        try:
            logger.info(f"Trying candidate model: {candidate}")
            model = genai.GenerativeModel(candidate)
            response = model.generate_content("Test")
            logger.info(f"Successfully found working model: {candidate}")
            return candidate
        except Exception as e:
            logger.warning(f"Candidate model {candidate} failed: {str(e)}")
            continue
    
    # Use legacy model name as last resort
    logger.warning("All model attempts failed, using legacy gemini-pro as final attempt")
    return "gemini-pro"

# Gemini agent implementation
def create_gemini_agent(model: str = 'gemini-1.5-pro-latest'):
    """Create a Gemini agent for project content generation"""
    # Get a working model
    working_model = get_available_model(model)
    logger.info(f"Creating agent with model: {working_model}")
    
    # Configure Google Search as a tool if using Gemini 2.0+ models
    # Note: These are model tools for Gemini API, not agent tools for pydantic-ai
    model_tools = []  # For the Gemini model itself, not for the Agent constructor
    if ENABLE_SEARCH_GROUNDING and '2.' in working_model:  # Check if we're using Gemini 2.x models
        try:
            logger.info("Setting up Google Search grounding for Gemini 2.0+ model")
            google_search_tool = Tool(google_search=GoogleSearch())
            model_tools = [google_search_tool]
        except Exception as e:
            logger.warning(f"Failed to set up Google Search grounding: {str(e)}")
    
    # Define the agent with Gemini model and structured output type
    agent_kwargs = {
        "model": working_model,
        "deps_type": ProjectInfo,
        "output_type": ProjectOutput,
        "system_prompt": (
            "You are a professional software engineer and technical documentation specialist. "
            "Your task is to create comprehensive project documentation and guidance based on "
            "the project information provided. Focus on best practices, technical accuracy, and "
            "providing actionable guidance. Use the most current and up-to-date information "
            "available about frameworks, libraries, and best practices."
        )
    }
    
    # Create model settings with the tools we want to use
    try:
        model_settings = GeminiModelSettings(
            temperature=0.2,
            top_p=0.95,
            top_k=40,
            max_output_tokens=16384
        )
        
        # Add tools to model_settings (not to Agent constructor)
        if model_tools and hasattr(model_settings, 'tools'):
            model_settings.tools = model_tools
            logger.info("Added search grounding tools to model settings")
        
        # Add model_settings to agent_kwargs
        agent_kwargs["model_settings"] = model_settings
    except Exception as e:
        logger.warning(f"Failed to create model settings: {str(e)}")
    
    logger.info(f"Creating agent with parameters: {', '.join(agent_kwargs.keys())}")
    content_agent = Agent(**agent_kwargs)
    
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
        - Appropriate best practices (using the most current information available)
        - Latest relevant tooling, frameworks, and extensions
        - Documentation needs with up-to-date reference links
        
        For frameworks and libraries, make sure to suggest the latest stable versions.
        Use Google Search when needed to get the most current and accurate information.
        Make sure all technical information and references are current and accurate.
        
        Provide thorough, actionable documentation suitable for a professional software team.
        """
    
    return content_agent

# Define template fetch and processing agent
def create_template_agent(model: str = 'gemini-1.5-flash-latest'):
    """Create a Gemini agent for template processing"""
    # Get a working model
    working_model = get_available_model(model)
    logger.info(f"Creating template agent with model: {working_model}")
    
    # Create model settings with increased token limit
    try:
        model_settings = GeminiModelSettings(
            temperature=0.2,
            top_p=0.95,
            top_k=40,
            max_output_tokens=16384,  # Increased token limit for more detailed template processing
        )
        
        # Configure Google Search as a tool if using Gemini 2.0+ models
        # Note: These are model tools for Gemini API, not agent tools for pydantic-ai
        model_tools = []  # For the Gemini model itself, not for the Agent constructor
        if ENABLE_SEARCH_GROUNDING and '2.' in working_model:  # Check if we're using Gemini 2.x models
            try:
                logger.info("Setting up Google Search grounding for template agent")
                google_search_tool = Tool(google_search=GoogleSearch())
                model_tools = [google_search_tool]
                
                # Handle different versions of the API
                if hasattr(model_settings, 'tools'):
                    model_settings.tools = model_tools
                    logger.info("Added search grounding tools to model settings")
                else:
                    logger.info("This version of the API doesn't support tools in model settings")
            except Exception as e:
                logger.warning(f"Failed to set up Google Search grounding for template agent: {str(e)}")
                model_tools = []  # Reset to empty list, not None
    except Exception as e:
        logger.warning(f"Failed to create model settings for template agent: {str(e)}")
        # Create fallbacks
        model_settings = None
    
    # Define base agent parameters
    agent_kwargs = {
        "model": working_model,  # Use a faster model for template processing
        "deps_type": dict,  # Use dictionary for template context
        "output_type": dict, # Return processed template
        "system_prompt": (
            "You are a template processor specialized in working with software project templates. "
            "Your job is to process template files, replace placeholders, and ensure the templates "
            "are correctly formatted for the project context. Use current technology and patterns."
        )
    }
    
    # Add model_settings to agent_kwargs if available
    if model_settings is not None:
        agent_kwargs["model_settings"] = model_settings
        
    logger.info(f"Creating template agent with parameters: {', '.join(agent_kwargs.keys())}")
    template_agent = Agent(**agent_kwargs)
    
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
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Verify configuration with API connectivity test
    try:
        # Get available models to verify connectivity
        test_result = get_available_model()
        logger.info(f"Gemini API connection successful. Using model: {test_result}")
        return True
    except Exception as e:
        logger.error(f"Gemini API connection test failed: {str(e)}")
        # Don't raise exception here - we'll let the main function handle it
        return False


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
    # Validate input parameters
    if not isinstance(content, str):
        logger.warning(f"Expected string content but got {type(content)}, converting to string")
        try:
            content = str(content) if content is not None else ""
        except Exception as e:
            logger.error(f"Failed to convert content to string: {str(e)}")
            return ""
    
    if not isinstance(placeholder_format, str):
        logger.warning(f"Invalid placeholder format: {placeholder_format}, using default")
        placeholder_format = "${%s}"
    
    if not isinstance(placeholder_vars, list):
        logger.warning(f"Expected list of placeholder variables but got {type(placeholder_vars)}, using defaults")
        placeholder_vars = ["project_name", "repo_org", "project_type", "programming_language"]
    
    try:
        # Create a mapping of variable names and their placeholder replacements
        replacements = {
            var_name: placeholder_format % var_name 
            for var_name in placeholder_vars 
            if isinstance(var_name, str)  # Only use string variable names
        }
        
        # Replace all concrete values with their placeholders
        template_content = content
        for var_name, placeholder in replacements.items():
            # Valid placeholder variable names we support
            if var_name in ["project_name", "repo_org", "project_type", "programming_language"]:
                template_content = template_content.replace(f"{var_name}", placeholder)
                
        return template_content
    except Exception as e:
        logger.error(f"Error in create_template_with_placeholders: {str(e)}")
        # Return original content if placeholder replacement fails
        return content


def generate_content(project_prompt: str, repo_org: str, project_name: str, model: str,
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
        
        # Prepare model settings for more comprehensive output
        try:
            model_settings = GeminiModelSettings(
                temperature=0.2,  # Low temperature for more predictable output
                top_p=0.95,       # High top_p for diverse but relevant responses
                top_k=40,         # Standard top_k value
                max_output_tokens=16384,  # Increased token limit for more detailed documentation
            )
            
            # For Gemini 2.0+ models, add tool configuration for Search Grounding
            if ENABLE_SEARCH_GROUNDING and '2.' in model:
                try:
                    logger.info("Configuring Search grounding in model settings")
                    google_search_tool = Tool(google_search=GoogleSearch())
                    
                    # Handle different versions of the API
                    if hasattr(model_settings, 'tools'):
                        model_settings.tools = [google_search_tool]
                        logger.info("Added search grounding tools to model settings")
                    else:
                        logger.info("This version of the API doesn't support tools in model settings")
                except Exception as e:
                    logger.warning(f"Failed to configure Search grounding in model settings: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to create model settings: {str(e)}")
            # Create a fallback model settings object
            model_settings = None
            
        # Create and configure the agent
        content_agent = create_gemini_agent(model)
        
        # Run the agent with the project info
        logger.info(f"Generating content for project '{project_name}'...")
        try:
            # Create the run arguments based on whether model_settings is available
            run_args = {
                "deps": project_info
            }
            
            if model_settings is not None:
                run_args["model_settings"] = model_settings
                
            # Log what we're doing for easier debugging
            logger.info(f"Running content agent with arguments: {', '.join(run_args.keys())}")
                
            # Run the agent with the appropriate arguments
            result = content_agent.run_sync(
                "Generate comprehensive documentation and project setup guidance with current best practices",
                **run_args
            )
            
            # Verify result is not None
            if result is None:
                raise ValueError("Agent returned None result")
                
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            raise ValueError(f"Failed to generate content: {str(e)}")
        
        # Check for and log any grounding metadata (Search results used)
        grounding_sources = []
        search_queries = []
        try:
            if (hasattr(result, 'candidate') and result.candidate is not None and 
                hasattr(result.candidate, 'grounding_metadata') and 
                result.candidate.grounding_metadata is not None):
                
                logger.info("Response included grounding metadata from Google Search")
                
                # Extract search queries if available
                if (hasattr(result.candidate.grounding_metadata, 'web_search_queries') and 
                    result.candidate.grounding_metadata.web_search_queries is not None):
                    try:
                        # Safely convert to list, handling any iterable issues
                        if hasattr(result.candidate.grounding_metadata.web_search_queries, '__iter__'):
                            search_queries = list(result.candidate.grounding_metadata.web_search_queries)
                        else:
                            # Handle the case where web_search_queries exists but is not iterable
                            search_queries = [str(result.candidate.grounding_metadata.web_search_queries)]
                        logger.info(f"Search queries used: {search_queries}")
                    except Exception as e:
                        logger.warning(f"Error processing search queries: {str(e)}")
                        search_queries = []
                
                # Extract grounding sources if available
                if (hasattr(result.candidate.grounding_metadata, 'grounding_chunks') and 
                    result.candidate.grounding_metadata.grounding_chunks is not None):
                    
                    try:
                        # Ensure grounding_chunks is iterable before attempting to iterate
                        chunks_iterable = result.candidate.grounding_metadata.grounding_chunks
                        if not hasattr(chunks_iterable, '__iter__'):
                            logger.warning("grounding_chunks is not iterable, converting to list")
                            # Handle non-iterable case
                            chunks_iterable = [chunks_iterable]
                            
                        for chunk in chunks_iterable:
                            if (hasattr(chunk, 'web') and chunk.web is not None and 
                                hasattr(chunk.web, 'uri') and chunk.web.uri is not None):
                                
                                grounding_sources.append({
                                    'uri': chunk.web.uri,
                                    'title': chunk.web.title if hasattr(chunk.web, 'title') and chunk.web.title is not None else "Unknown"
                                })
                    except Exception as e:
                        logger.warning(f"Error processing grounding chunks: {str(e)}")
                        # Continue execution despite this error
                    
                    if grounding_sources:
                        logger.info(f"Found {len(grounding_sources)} grounding sources")
        except Exception as e:
            logger.warning(f"Error extracting grounding metadata: {str(e)}")
            logger.warning(f"Error details: {type(e).__name__}, {e}, {e.__traceback__.tb_lineno}")
        
        # Extract the structured output with careful validation
        main_content = {}
        
        # Make sure we have a result with an output
        if result is not None and hasattr(result, 'output') and result.output is not None:
            # For each field in the expected output, check if it exists before adding
            for field_name in ["readme_content", "best_practices", "suggested_extensions", 
                              "documentation_source", "copilot_instructions"]:
                if hasattr(result.output, field_name):
                    field_value = getattr(result.output, field_name)
                    if field_value is not None:
                        main_content[field_name] = field_value
                    else:
                        main_content[field_name] = "" if field_name == "readme_content" else []
                else:
                    # Provide default values for missing fields
                    main_content[field_name] = "" if field_name == "readme_content" else []
        else:
            logger.error("Invalid result or missing output structure")
            main_content = {
                "readme_content": "Error: Failed to generate content.",
                "best_practices": [],
                "suggested_extensions": [],
                "documentation_source": [],
                "copilot_instructions": ""
            }
        
        # Process content to add placeholders if requested
        if create_with_placeholders:
            for key in main_content:
                if isinstance(main_content[key], str):
                    main_content[key] = create_template_with_placeholders(
                        main_content[key], placeholder_format, placeholder_vars
                    )
        
        # Add search grounding metadata to the output if available
        if grounding_sources:
            main_content["grounding_sources"] = grounding_sources
            main_content["search_queries"] = search_queries
        
        # Extract project type and programming language with validation
        project_type = "Unknown"
        programming_language = "Unknown"
        
        try:
            if result is not None and hasattr(result, 'output') and result.output is not None:
                if hasattr(result.output, 'project_type') and result.output.project_type is not None:
                    project_type = str(result.output.project_type)
                    
                if hasattr(result.output, 'programming_language') and result.output.programming_language is not None:
                    programming_language = str(result.output.programming_language)
        except Exception as e:
            logger.error(f"Error extracting project type or language: {str(e)}")
        
        # Safely encode the main content to JSON with error handling
        main_content_json = "{}"
        try:
            main_content_json = json.dumps(main_content)
        except TypeError as e:
            logger.error(f"JSON serialization error: {str(e)}")
            # Try to fix non-serializable objects
            sanitized_content = {}
            for key, value in main_content.items():
                try:
                    # Test if this item can be serialized
                    json.dumps({key: value})
                    sanitized_content[key] = value
                except (TypeError, OverflowError):
                    # Convert non-serializable value to string representation
                    sanitized_content[key] = str(value)
            
            try:
                main_content_json = json.dumps(sanitized_content)
            except Exception as nested_e:
                logger.error(f"Failed to sanitize content for JSON: {str(nested_e)}")
                main_content_json = json.dumps({"error": "Failed to serialize response content"})
        
        # Return the result as a dictionary with safe values
        # Note: All values must be strings for Terraform external data source
        return {
            "main": main_content_json,
            "project_type": project_type,
            "programming_language": programming_language,
            "used_search_grounding": str(bool(grounding_sources)).lower()  # Convert boolean to string "true"/"false"
        }
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        # Get the stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Stack trace: {stack_trace}")
        # Return error information, stack trace, and fallback empty content
        return {
            "error": str(e),
            "stack_trace": stack_trace,
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
        gemini_model = input_data.get('gemini_model', 'gemini-1.5-pro-latest')  # Get model name from input
        
        # Clean model name if needed
        if gemini_model and isinstance(gemini_model, str) and gemini_model.startswith('google-gla:'):
            gemini_model = gemini_model.split(':', 1)[1]
            
        # Log the model being used
        logger.info(f"Using Gemini model: {gemini_model}")
        
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
        
        # Configure API and test connection
        api_success = configure_gemini_api()
        if not api_success:
            error_msg = "Failed to establish connection with Gemini API. Check your API key and network connection."
            logger.error(error_msg)
            print(json.dumps({
                "error": error_msg,
                "stack_trace": traceback.format_exc(),
                "main": json.dumps({"error": error_msg}),
                "project_type": "Unknown",
                "programming_language": "Unknown"
            }))
            sys.exit(0)
        
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
                    
                    try:
                        # Create and run template agent
                        template_agent = create_template_agent(input_data.get('template_model', 'gemini-1.5-flash-latest'))
                        
                        # Run initial template analysis with error handling
                        try:
                            template_result = template_agent.run_sync(
                                f"Analyze and process template for {project_name}",
                                deps=template_context
                            )
                        except Exception as e:
                            logger.warning(f"Error in initial template analysis: {str(e)}")
                            template_result = None
                        
                        # Get detailed template analysis with error handling
                        try:
                            analysis = template_agent.run_sync(
                                "Analyze the template structure",
                                deps=template_context,
                                tool_choice="analyze_template",
                                tool_params={"template_content": template_content}
                            )
                        except Exception as e:
                            logger.warning(f"Error in template structure analysis: {str(e)}")
                            # Create a fallback analysis result
                            analysis = type('AnalysisResult', (), {
                                'output': {
                                    'identified_vars': [],
                                    'has_placeholders': False,
                                    'template_length': len(template_content)
                                }
                            })
                    except Exception as e:
                        logger.error(f"Critical error in template processing: {str(e)}")
                        # Create fallback objects
                        template_result = None
                        analysis = type('AnalysisResult', (), {
                            'output': {
                                'identified_vars': [],
                                'has_placeholders': False,
                                'template_length': len(template_content),
                                'error': str(e)
                            }
                        })
                    
                    # Set result with the template content and analysis
                    project_type = "Unknown"
                    programming_language = "Unknown"
                    
                    # Try to extract project type and language from template
                    try:
                        template_data = json.loads(template_content)
                        project_type = template_data.get("project_type", "Unknown")
                        programming_language = template_data.get("programming_language", "Unknown")
                    except json.JSONDecodeError:
                        # Template might not be in JSON format
                        logger.warning("Template is not in JSON format, using default values")
                    except Exception as e:
                        logger.warning(f"Unexpected error parsing template: {str(e)}")
                    
                    # Safely prepare analysis output for JSON serialization
                    analysis_output = {}
                    try:
                        if analysis is not None and hasattr(analysis, 'output'):
                            if analysis.output is not None:
                                analysis_output = analysis.output
                            else:
                                logger.warning("Analysis output is None")
                        else:
                            logger.warning("Analysis object is missing or has no output attribute")
                    except Exception as e:
                        logger.warning(f"Error accessing analysis output: {str(e)}")
                    
                    result = {
                        "main": template_content,
                        "project_type": project_type,
                        "programming_language": programming_language,
                        "template_analysis": json.dumps(analysis_output)
                    }
                else:
                    # Just return the raw template
                    result = {
                        "main": template_content,
                        "project_type": "Unknown", 
                        "programming_language": "Unknown"
                    }
            except Exception as e:
                # Capture and log the stack trace
                stack_trace = traceback.format_exc()
                logger.error(f"Error processing template: {str(e)}")
                logger.error(f"Stack trace: {stack_trace}")
                # Fall back to generating content if template fetching fails
                try:
                    result = generate_content(
                        project_prompt=project_prompt,
                        repo_org=repo_org,
                        project_name=project_name,
                        model=input_data.get('template_model', 'gemini-1.5-flash-latest'),
                        create_with_placeholders=create_with_placeholders,
                        placeholder_format=placeholder_format,
                        placeholder_vars=placeholder_vars
                    )
                    # Add the original error and stack trace to the result
                    if isinstance(result, dict) and not "error" in result:
                        result["template_processing_error"] = str(e)
                        result["template_processing_stack_trace"] = stack_trace
                except Exception as fallback_error:
                    # If even the fallback fails, return a comprehensive error
                    fallback_stack_trace = traceback.format_exc()
                    result = {
                        "error": f"Template processing failed AND fallback generation failed: {str(e)} -> {str(fallback_error)}",
                        "stack_trace": f"ORIGINAL ERROR:\n{stack_trace}\n\nFALLBACK ERROR:\n{fallback_stack_trace}",
                        "main": json.dumps({"error": "Multiple cascading failures occurred"}),
                        "project_type": "Unknown",
                        "programming_language": "Unknown"
                    }
        else:
            # Generate content with Gemini
            result = generate_content(
                project_prompt=project_prompt,
                repo_org=repo_org,
                project_name=project_name,
                model=gemini_model,  # Use the main model parameter from the module
                create_with_placeholders=create_with_placeholders,
                placeholder_format=placeholder_format,
                placeholder_vars=placeholder_vars
            )
        
        # Return result as JSON to stdout
        print(json.dumps(result))
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        stack_trace = traceback.format_exc()
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        print(json.dumps({
            "error": f"Invalid JSON input: {str(e)}",
            "stack_trace": stack_trace
        }))
        sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        print(json.dumps({
            "error": str(e),
            "stack_trace": stack_trace
        }))
        sys.exit(0)  # Exit with 0 to provide error in JSON format for Terraform


if __name__ == "__main__":
    main()
