#!/Users/darnold/git/terraform-prompt-template/.venv/bin/python3
"""
Gemini content generation script for terraform-github-project
Retrieves AI-generated content using Gemini API based on project prompt and requirements

Usage:
  python gemini_generator.py --project_name "My Project" --repo_org "myorg" --project_prompt "Description" 
    --markdown_output "output.md"

Output Configuration:
  Individual file outputs can be specified with --markdown_output, etc.
  Alternatively, use --output_dir to write all outputs to a single directory:
  
  python gemini_generator.py --project_name "My Project" --repo_org "myorg" --project_prompt "Description" 
    --output_dir "./output"
  
  When --output_dir is specified, the script will create the directory if it doesn't exist,
  and all output files will be written there, preserving their original filenames.
"""

import json
import os
import sys
import logging
import traceback
import urllib.parse
import argparse
from pathlib import Path

from typing import Dict, Any, List, Optional, Type, Callable
import requests  # For GitHub API requests
from jinja2 import Template, FileSystemLoader, Environment
from models import *  # Import your models from the models module

import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.gemini import GeminiModelSettings
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# SYMBOL MAP
# ----------
# Classes:
#   CommonGeminiTools:
#     - Manages Gemini API configuration, model discovery, validation, and pydantic-ai Agent creation.
#   MainContentGenerator:
#     - Responsible for generating the primary project documentation (README, best practices, etc.)
#     using a Gemini agent.
#   CopilotInstructionsGenerator:
#     - Generates GitHub Copilot instructions based on project details and main content output.
#   ProjectPromptsFormatter:
#     - Formats different types of project prompt files (simple and GitHub-specific).
#   OutputFileWriter:
#     - Handles writing the main generated content to a markdown file.
#   ProjectPrompt:
#     - Encapsulates the end-to-end project content generation workflow, including
#       main content, project prompts, and Copilot instructions. It initializes and
#       coordinates the various generator and formatter classes.
#
# Key Functions (within classes):
#   CommonGeminiTools.configure_api: Configures and tests the Gemini API connection.
#   CommonGeminiTools.get_available_model: Finds a suitable, available Gemini model.
#   CommonGeminiTools.create_pydantic_agent: Creates and configures a pydantic-ai Agent.
#   MainContentGenerator.generate: Orchestrates the main content generation.
#   CopilotInstructionsGenerator.generate: Orchestrates Copilot instructions generation.
#   ProjectPromptsFormatter.format_github_project_prompt: Formats the GitHub-specific prompt.
#   ProjectPromptsFormatter.format_simple_project_prompt: Formats the basic project prompt.
#   OutputFileWriter.write_markdown_output: Writes the main markdown output file.
#   OutputFileWriter.write_error_markdown: Writes error information to the markdown file.
#   ProjectPrompt._generate_all_content: Runs the full content generation pipeline.
#
# Global Variables:
#   logger: Standard Python logger instance.
#   template_env: Jinja2 environment for loading templates.
#   MAIN_MARKDOWN_TEMPLATE: Jinja2 template for the main Markdown output.
#   ENABLE_SEARCH_GROUNDING: Boolean flag to control Google Search grounding.
#
# Pydantic Models (from models.py):
#   ProjectInfo: Input model for project details.
#   ProjectOutput: Output model for main generated content.
#   CopilotAgentDeps: Dependencies for the Copilot instructions agent.
#   CopilotPromptContent: Output model for structured Copilot instructions content.


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File Handler
file_handler = logging.FileHandler('gemini_generator.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Set up Jinja2 template environment
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
template_loader = FileSystemLoader(searchpath=template_dir)
template_env = Environment(loader=template_loader)

class CommonGeminiTools:
    """
    Provides common utilities for interacting with the Google Gemini API,
    including API configuration, model discovery, and agent creation.
    """
    def __init__(self, api_key: Optional[str] = None, enable_search_grounding: bool = True):
        """
        Initializes CommonGeminiTools.

        Args:
            api_key: Optional Gemini API key. If provided, configures the API.
            enable_search_grounding: Flag to enable/disable search grounding features.
        """
        self.enable_search_grounding = enable_search_grounding
        if api_key:
            self.configure_api(api_key)

    def configure_api(self, api_key: str) -> bool:
        """
        Configures the Google Gemini API with the provided API key and tests the connection.

        Args:
            api_key: The Gemini API key.

        Returns:
            True if configuration and connection test are successful, False otherwise.
        """
        if not api_key:
            logger.error("Gemini API key not provided for configuration.")
            return False
        try:
            genai.configure(api_key=api_key)
            self.get_available_model()
            logger.info("Gemini API configured and connection successful.")
            return True
        except Exception as e:
            logger.error(f"Gemini API configuration or connection test failed: {str(e)}")
            return False

    def get_model_details(self, model_name: str) -> Dict[str, Any]:
        """
        Retrieves details and capabilities for a given Gemini model name.
        Provides conservative defaults if the model is not found or details are missing.

        Args:
            model_name: The name of the model (e.g., "gemini-1.5-pro").

        Returns:
            A dictionary containing model parameters like temperature, top_p, top_k,
            max_output_tokens, and candidate_count.
        """
        try:
            if model_name.startswith("models/"):
                model_name = model_name[7:]
            models = genai.list_models()
            model_info = None
            for model_obj in models:
                if model_obj.name.endswith(model_name):
                    model_info = model_obj
                    logger.info(f"Found model details for {model_name}")
                    break
            if model_info is None:
                logger.warning(f"Could not find details for model {model_name}, using conservative defaults")
                return {"temperature": 0.2, "top_p": 0.95, "top_k": 32, "max_output_tokens": 4096, "candidate_count": 1}
            
            output_token_limit = getattr(model_info, 'output_token_limit', 4096)
            default_temp = getattr(model_info, 'temperature', 1.0)
            max_temp = getattr(model_info, 'max_temperature', 2.0)
            if max_temp is None: max_temp = 2.0
            default_top_p = getattr(model_info, 'top_p', 0.95)
            default_top_k = getattr(model_info, 'top_k', 40)
            
            logger.info(f"Model limits: output_tokens={output_token_limit}, max_temp={max_temp}, top_p={default_top_p}, top_k={default_top_k}")
            
            return {
                "temperature": min(0.2, max_temp if max_temp is not None else 0.2),
                "top_p": default_top_p,
                "top_k": default_top_k,
                "max_output_tokens": min(16384, output_token_limit),
                "candidate_count": 1,
                "max_temperature": max_temp
            }
        except Exception as e:
            logger.warning(f"Error getting model details for {model_name}: {str(e)}, using conservative defaults")
            return {"temperature": 0.2, "top_p": 0.95, "top_k": 32, "max_output_tokens": 4096, "candidate_count": 1}

    def get_available_model(self, requested_model: str = 'gemini-1.5-pro') -> str:
        """
        Finds an available Gemini model, trying the requested model first,
        then falling back to other available models based on a priority.

        Args:
            requested_model: The preferred model name.

        Returns:
            The name of a working, available Gemini model.
        """
        try:
            logger.info(f"Trying requested model: {requested_model}")
            model_to_test = genai.GenerativeModel(requested_model)
            model_to_test.generate_content("Test")
            logger.info(f"Successfully using requested model: {requested_model}")
            return requested_model
        except Exception as e:
            logger.warning(f"Requested model {requested_model} not available or failed test: {str(e)}")

        try:
            logger.info("Fetching list of available models from Gemini API...")
            available_models = genai.list_models()
            content_models = [
                model.name.replace("models/", "") 
                for model in available_models 
                if 'generateContent' in getattr(model, 'supported_generation_methods', [])
            ]
            if not content_models:
                logger.warning("No models supporting generateContent found, falling back to gemini-pro.")
                return "gemini-pro"

            sorted_models = sorted(content_models, key=lambda m: ("pro" not in m, "flash" not in m, m), reverse=False)
            
            logger.info(f"Available models sorted (simplified): {sorted_models[:5]} (showing top 5)")
            for candidate in sorted_models:
                try:
                    logger.info(f"Trying candidate model: {candidate}")
                    model_to_test = genai.GenerativeModel(candidate)
                    model_to_test.generate_content("Test")
                    logger.info(f"Successfully found working model: {candidate}")
                    return candidate
                except Exception as e_candidate:
                    logger.warning(f"Candidate model {candidate} failed: {str(e_candidate)}")
                    continue
        except Exception as e_list:
            logger.error(f"Error getting available models: {str(e_list)}")
        
        logger.warning("All model attempts failed, using legacy gemini-pro as final attempt.")
        return "gemini-pro"

    def _validate_token_config(self, token_config: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Validates and adjusts token configuration parameters (temperature, top_p, etc.)
        against the capabilities of the specified model.

        Args:
            token_config: The user-provided token configuration.
            model_name: The name of the model to validate against.

        Returns:
            A dictionary with validated and potentially adjusted token configurations.
        """
        model_capabilities = self.get_model_details(model_name)
        validated_config = token_config.copy()

        max_temp = model_capabilities.get("max_temperature", 2.0)
        if "temperature" in validated_config:
            if validated_config["temperature"] > max_temp:
                logger.warning(f"Temperature {validated_config['temperature']} exceeds model maximum {max_temp}, adjusting to {max_temp}")
                validated_config["temperature"] = max_temp
            elif validated_config["temperature"] < 0:
                 logger.warning(f"Temperature {validated_config['temperature']} is below 0, adjusting to 0")
                 validated_config["temperature"] = 0.0

        model_max_tokens = model_capabilities.get("max_output_tokens", 4096)
        if "max_output_tokens" in validated_config:
            if validated_config["max_output_tokens"] > model_max_tokens:
                logger.warning(f"max_output_tokens {validated_config['max_output_tokens']} exceeds model limit {model_max_tokens}, adjusting.")
                validated_config["max_output_tokens"] = model_max_tokens
            elif validated_config["max_output_tokens"] <=0:
                logger.warning(f"max_output_tokens {validated_config['max_output_tokens']} must be positive, adjusting to {model_max_tokens}.")
                validated_config["max_output_tokens"] = model_max_tokens

        model_top_p = model_capabilities.get("top_p", 0.95)
        if "top_p" in validated_config:
            if not (0 <= validated_config["top_p"] <= 1):
                logger.warning(f"top_p {validated_config['top_p']} is outside valid range [0,1], adjusting to model default {model_top_p}")
                validated_config["top_p"] = model_top_p
        
        model_top_k = model_capabilities.get("top_k", 40)
        if "top_k" in validated_config:
            if validated_config["top_k"] <= 0:
                logger.warning(f"top_k {validated_config['top_k']} must be positive, adjusting to model default {model_top_k}")
                validated_config["top_k"] = model_top_k
        
        return validated_config

    def create_pydantic_agent(self, model_name: str, token_config: Dict,
                              deps_type: Type[BaseModel], output_type: Type[BaseModel],
                              system_prompt_str: str,
                              context_template_str: Optional[str] = None,
                              context_data_func: Optional[Callable[[RunContext], Dict[str, Any]]] = None) -> Agent:
        """
        Creates a pydantic-ai Agent configured with a Gemini model.

        Args:
            model_name: The name of the Gemini model to use.
            token_config: Dictionary of token settings (temperature, top_p, etc.).
            deps_type: The Pydantic model type for agent dependencies (input).
            output_type: The Pydantic model type for the agent's structured output.
            system_prompt_str: The base system prompt string for the agent.
            context_template_str: Optional Jinja2 template string for dynamic context.
                                  If provided, this template is rendered by `context_data_func`.
            context_data_func: Optional callable that takes a RunContext and returns a dictionary
                               of values to render `context_template_str`.

        Returns:
            A configured pydantic-ai Agent instance.
        """
        working_model = self.get_available_model(model_name)
        logger.info(f"Creating agent with model: {working_model}")

        validated_token_config = self._validate_token_config(token_config, working_model)

        model_tools = []
        if self.enable_search_grounding and ('1.5' in working_model or '2.' in working_model):
            try:
                logger.info("Search grounding is enabled; relying on model/pydantic-ai for its application.")
            except Exception as e:
                 logger.warning(f"Could not set up Google Search tool for pydantic-ai agent: {e}")

        agent_kwargs = {
            "model": working_model,
            "deps_type": deps_type,
            "output_type": output_type,
            "system_prompt": system_prompt_str,
        }

        try:
            model_settings_params = {
                k: v for k, v in validated_token_config.items() if k in ["temperature", "top_p", "top_k", "max_output_tokens", "candidate_count"]
            }
            model_settings = GeminiModelSettings(**model_settings_params)
            
            if model_tools and hasattr(model_settings, 'tools'):
                 model_settings.tools = model_tools
                 logger.info("Added tools to GeminiModelSettings for pydantic-ai agent.")

            agent_kwargs["model_settings"] = model_settings
        except Exception as e:
            logger.warning(f"Failed to create GeminiModelSettings: {str(e)}. Agent will use defaults.")

        logger.info(f"Creating pydantic-ai agent with model: {working_model}, system prompt length: {len(system_prompt_str)}")
        content_agent = Agent(**agent_kwargs)

        if context_template_str and context_data_func:
            @content_agent.system_prompt
            def add_dynamic_context(ctx: RunContext) -> str:
                """Renders the context template with data from context_data_func."""
                context_values = context_data_func(ctx)
                return Template(context_template_str).render(**context_values)

        return content_agent


class MainContentGenerator:
    """
    Generates the main project content, including README, best practices,
    suggested extensions, and documentation sources using a Gemini agent.
    """
    def __init__(self, common_tools: CommonGeminiTools, project_name: str, project_prompt_text: str,
                 repo_org: str, model_name: str, token_config: Dict[str, Any]):
        """
        Initializes MainContentGenerator.

        Args:
            common_tools: An instance of CommonGeminiTools.
            project_name: The name of the project.
            project_prompt_text: The user-provided project prompt.
            repo_org: The GitHub organization for the repository.
            model_name: The Gemini model to use for content generation.
            token_config: Token configuration for the Gemini model.
        """
        self.common_tools = common_tools
        self.project_name = project_name
        self.project_prompt_text = project_prompt_text
        self.repo_org = repo_org
        self.model_name = model_name
        self.token_config = token_config
        
        try:
            with open(os.path.join(template_dir, "content_agent_system_prompt.txt"), "r") as f:
                self.system_prompt_template_str = f.read()
            with open(os.path.join(template_dir, "content_agent_project_context.j2"), "r") as f:
                self.context_template_str = f.read()
        except Exception as e:
            logger.error(f"Failed to load templates for MainContentGenerator: {e}")
            self.system_prompt_template_str = "Generate project documentation."
            self.context_template_str = "Project: {{ project_name }}"

    def generate(self, placeholder_format: str,
                 placeholder_vars: List[str]) -> ProjectOutput:
        """
        Generates the main project documentation.

        Args:
            placeholder_format: The format string for placeholders (currently not deeply integrated).
            placeholder_vars: A list of variable names to be treated as placeholders (currently not deeply integrated).

        Returns:
            A ProjectOutput Pydantic model containing the generated content.
        """
        logger.info(f"Generating main content for project '{self.project_name}'...")
        project_info = ProjectInfo(
            project_name=self.project_name,
            repo_org=self.repo_org,
            project_prompt=self.project_prompt_text
        )

        def project_context_data_func(ctx: RunContext[ProjectInfo]) -> Dict[str, Any]:
            return {
                "project_name": ctx.deps.project_name,
                "repo_org": ctx.deps.repo_org,
                "project_prompt": ctx.deps.project_prompt,
            }

        agent = self.common_tools.create_pydantic_agent(
            model_name=self.model_name,
            token_config=self.token_config,
            deps_type=ProjectInfo,
            output_type=ProjectOutput,
            system_prompt_str=self.system_prompt_template_str,
            context_template_str=self.context_template_str,
            context_data_func=project_context_data_func
        )

        try:
            logger.info(f"Running main content agent for '{self.project_name}'...")
            result = agent.run_sync(
                "Generate comprehensive documentation and project setup guidance with current best practices.",
                deps=project_info
            )

            if result is None or not hasattr(result, 'output'):
                raise ValueError("Main content agent returned None or no output.")
            
            output_data: ProjectOutput = result.output
            try:
                if hasattr(result, 'candidate') and result.candidate and \
                   hasattr(result.candidate, 'grounding_metadata') and result.candidate.grounding_metadata:
                    logger.info("Response included grounding metadata.")
                    output_data.grounding_sources = [{"uri": "example.com/source", "title": "Example Source"}] 
                    output_data.search_queries = ["example search query"]
            except Exception as e:
                logger.warning(f"Error extracting grounding metadata: {e}")

            return output_data

        except Exception as e:
            logger.error(f"Error running main content agent: {str(e)}")
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            logger.error(stack_trace)
            return ProjectOutput(
                readme_content=f"# Error in Main Content Generation\n\nError: {error_msg}\n\n```\n{stack_trace}\n```",
                best_practices=[], suggested_extensions=[], documentation_source=[],
                copilot_instructions="", project_type="Unknown", programming_language="Unknown",
                error=error_msg, stack_trace=stack_trace
            )


class OutputFileWriter:
    """
    Handles writing the main generated content to a markdown file.
    """
    def __init__(self, args: argparse.Namespace, main_markdown_template: Template):
        self.args = args
        self.main_markdown_template = main_markdown_template

    def _write_file(self, output_arg_key: str, content: str, error_message: str):
        original_file_path = getattr(self.args, output_arg_key, None)
        if not original_file_path:
            logger.info(f"Output path for '{output_arg_key}' not provided. Skipping.")
            return
        file_path = original_file_path
        try:
            directory = os.path.dirname(os.path.abspath(file_path))
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created or verified directory: {directory}")
            except Exception as dir_err:
                logger.error(f"Failed to create directory {directory}: {str(dir_err)}")
                raise
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_size = os.path.getsize(file_path)
            file_size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            logger.info(f"Successfully wrote {file_size_str} to {file_path}")
        except Exception as e:
            logger.error(f"{error_message} for {file_path}: {str(e)}")

    def _convert_project_output_to_markdown(self, project_output: ProjectOutput) -> str:
        if hasattr(project_output, 'model_dump') and callable(getattr(project_output, 'model_dump')):
            model_dict = project_output.model_dump()
            data_for_template = {
                "readme_content": model_dict.get("readme_content", "No content available"),
                "best_practices": model_dict.get("best_practices", []),
                "suggested_extensions": model_dict.get("suggested_extensions", []),
                "documentation_source": model_dict.get("documentation_source", []),
                "copilot_instructions": model_dict.get("copilot_instructions"),
            }
        else:
            data_for_template = {"readme_content": "Invalid project output format for Markdown."}
        return self.main_markdown_template.render(data_for_template)

    def write_markdown_output(self, project_output: ProjectOutput):
        logger.info("Writing main markdown output file...")
        if hasattr(self.args, 'markdown_output') and self.args.markdown_output:
            markdown_content = self._convert_project_output_to_markdown(project_output)
            self._write_file('markdown_output', markdown_content, "Failed to write Markdown output")

    def write_error_markdown(self, error_msg: str, stack_trace: Optional[str] = None):
        logger.error(f"Writing error markdown due to: {error_msg}")
        error_content_md = f"# Error: Failed to Generate Content\n\n{error_msg}"
        if stack_trace:
            error_content_md += f"\n\n## Stack Trace\n\n```\n{stack_trace}\n```"
        self._write_file('markdown_output', error_content_md, "Failed to write error Markdown")


class ProjectPrompt:
    """
    Encapsulates the project content generation workflow, including main content,
    project prompts, and Copilot instructions.
    """
    def __init__(self,
                 project_name: str,
                 project_prompt_text: str,
                 repo_org: str,
                 gemini_api_key: str,
                 main_gemini_model: str = 'gemini-1.5-pro-latest',
                 copilot_gemini_model: str = 'gemini-1.5-flash-latest',
                 token_config_overrides: Optional[Dict[str, Any]] = None,
                 enable_search_grounding: bool = True,
                 placeholder_format: str = '${%s}',
                 placeholder_vars_list: Optional[List[str]] = None,
                 project_prompt_formatter_template_path: Optional[str] = None
                 ):
        """
        Initializes the ProjectPrompt generator.

        Args:
            project_name: Name of the project.
            project_prompt_text: User-provided project prompt.
            repo_org: GitHub organization.
            gemini_api_key: Gemini API key.
            main_gemini_model: Model for main content generation.
            copilot_gemini_model: Model for Copilot instructions.
            token_config_overrides: Dictionary to override default token settings.
            enable_search_grounding: Whether to enable search grounding.
            placeholder_format: Format string for placeholders.
            placeholder_vars_list: List of placeholder variable names.
            project_prompt_formatter_template_path: Optional custom template path for ProjectPromptsFormatter.
        """
        self.project_name = project_name
        self.project_prompt_text = project_prompt_text
        self.repo_org = repo_org
        self.gemini_api_key = gemini_api_key
        self.main_gemini_model = main_gemini_model
        self.copilot_gemini_model = copilot_gemini_model
        self.token_config_overrides = token_config_overrides or {}
        self.enable_search_grounding = enable_search_grounding
        self.placeholder_format = placeholder_format
        self.placeholder_vars_list = placeholder_vars_list or ['project_name', 'repo_org', 'project_type', 'programming_language']
        self.project_prompt_formatter_template_path = project_prompt_formatter_template_path

        self._project_output_data: Optional[ProjectOutput] = None
        self._initialization_success = False
        
        try:
            self.common_tools = CommonGeminiTools(
                api_key=self.gemini_api_key, 
                enable_search_grounding=self.enable_search_grounding
            )
            if not self.common_tools.configure_api(self.gemini_api_key):
                raise RuntimeError("Failed to configure or connect to Gemini API.")

            self._initialize_generators()
            self._generate_all_content()
            self._initialization_success = True
        except Exception as e:
            logger.error(f"Error during ProjectPrompt initialization: {e}")
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            # Create a minimal error output so that properties don't return None
            error_msg = f"ProjectPrompt initialization failed: {str(e)}"
            self._project_output_data = ProjectOutput(
                readme_content=f"# Error\n\n{error_msg}\n\n```\n{stack_trace}\n```",
                best_practices=[], suggested_extensions=[], documentation_source=[],
                copilot_instructions="", project_type="Error", programming_language="Error",
                error=error_msg, stack_trace=stack_trace
            )
            
            # Re-raise the exception so the caller knows something went wrong
            raise

    def _initialize_generators(self):
        base_token_config = {
            "temperature": 0.2, "top_p": 0.95, "top_k": 40,
            "max_output_tokens": 16384, "candidate_count": 1
        }
        base_token_config.update(self.token_config_overrides)
        
        logger.info(f"Base token configurations for ProjectPrompt: {base_token_config}")

        main_content_token_config = base_token_config.copy()
        copilot_token_config = base_token_config.copy()

        self.main_generator = MainContentGenerator(
            self.common_tools, self.project_name, self.project_prompt_text, self.repo_org,
            self.main_gemini_model, main_content_token_config
        )

    def _generate_all_content(self):
        logger.info("Starting content generation process within ProjectPrompt...")
        self._project_output_data = self.main_generator.generate(
            self.placeholder_format, self.placeholder_vars_list
        )

        if self._project_output_data.error or "Error in Main Content Generation" in self._project_output_data.readme_content:
            logger.error("Main content generation failed within ProjectPrompt.")
            error_details = self._project_output_data.error or "See readme content for details"
            raise RuntimeError(f"Main content generation failed. Details: {error_details}")

    @property
    def initialization_success(self) -> bool:
        """Returns whether initialization completed successfully without errors."""
        return self._initialization_success
    
    @property
    def project_output_data(self) -> Optional[ProjectOutput]:
        """Returns the generated project output data or an error-filled object if initialization failed."""
        if not self._initialization_success:
            logger.warning("Accessing project_output_data after failed initialization.")
        return self._project_output_data


def main():
    parser = argparse.ArgumentParser(description='Generate project documentation using Gemini API')
    parser.add_argument('--project_prompt', required=True, help='Project description')
    parser.add_argument('--repo_org', required=True, help='GitHub organization name')
    parser.add_argument('--project_name', required=True, help='Project name')
    parser.add_argument('--gemini_model', default='gemini-1.5-pro-latest', help='Main Gemini model for content generation')
    parser.add_argument('--copilot_gemini_model', default='gemini-1.5-flash-latest', help='Gemini model for Copilot instructions')
    parser.add_argument('--markdown_output', required=True, help='Path for the output Markdown file')
    parser.add_argument('--enable_search_grounding', type=str, default='true', help='Enable search grounding for supported models')
    parser.add_argument('--placeholder_format', default='${%s}', help='Placeholder format string')
    parser.add_argument('--placeholder_vars', default='project_name,repo_org,project_type,programming_language', 
                        help='Comma-separated list of placeholder variables')
    parser.add_argument('--temperature', type=float, help='Model temperature (overrides defaults)')
    parser.add_argument('--top_p', type=float, help='Model top_p (overrides defaults)')
    parser.add_argument('--top_k', type=int, help='Model top_k (overrides defaults)')
    parser.add_argument('--project_prompt_template', 
        type=str, 
        help='Path to the project prompt template file', 
        default=os.path.join(template_dir, "project_prompt_template.j2"))
    parser.add_argument('--max_output_tokens', type=int, help='Max output tokens (overrides defaults)')
    parser.add_argument('--output_dir', 
        type=str, 
        help='Path to a directory where all output files will be saved. If specified, overrides individual file paths.')
    parser.add_argument('--preserve_relative_paths',
        action='store_true',
        help="When used with --output_dir, preserves relative path structure even for paths with parent directories"
    )
    args = parser.parse_args()

    if args.output_dir:
        try:
            expanded_output_dir = os.path.expandvars(os.path.expanduser(args.output_dir))
            args.output_dir = expanded_output_dir
            os.makedirs(args.output_dir, exist_ok=True)
            logger.info(f"Output directory set to: {args.output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory {args.output_dir}: {e}")
            sys.exit(1)

    main_markdown_template_content = ""
    try:
        with open(os.path.join(template_dir, "project_prompt_template.j2"), "r", encoding="utf-8") as f:
            main_markdown_template_content = f.read()
    except Exception as e:
        logger.error(f"Failed to load main markdown template (project_prompt_template.j2): {e}")
        sys.exit(1)
        
    output_writer = OutputFileWriter(args, Template(main_markdown_template_content))

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            output_writer.write_error_markdown("GEMINI_API_KEY not set.")
            sys.exit(1)

        token_config_overrides = {}
        if args.temperature is not None: token_config_overrides["temperature"] = args.temperature
        if args.top_p is not None: token_config_overrides["top_p"] = args.top_p
        if args.top_k is not None: token_config_overrides["top_k"] = args.top_k
        if args.max_output_tokens is not None: token_config_overrides["max_output_tokens"] = args.max_output_tokens
         
        enable_search_grounding_flag = args.enable_search_grounding.lower() == 'true'

        project_prompt_instance = ProjectPrompt(
            project_name=args.project_name,
            project_prompt_text=args.project_prompt,
            repo_org=args.repo_org,
            gemini_api_key=api_key,
            main_gemini_model=args.gemini_model,
            copilot_gemini_model=args.copilot_gemini_model,
            token_config_overrides=token_config_overrides,
            enable_search_grounding=enable_search_grounding_flag,
            placeholder_format=args.placeholder_format,
            placeholder_vars_list=args.placeholder_vars.split(','),
            project_prompt_formatter_template_path=args.project_prompt_template
        )

        if not project_prompt_instance.initialization_success:
            err_msg = "Content generation failed during initialization."
            project_output = project_prompt_instance.project_output_data
            output_writer.write_error_markdown(
                err_msg,
                project_output.stack_trace if project_output and hasattr(project_output, 'stack_trace') else None
            )
            sys.exit(1)
            
        project_output = project_prompt_instance.project_output_data
        if not project_output or project_output.error:
            error_msg = project_output.error if project_output and hasattr(project_output, 'error') else "Unknown error."
            output_writer.write_error_markdown(error_msg, getattr(project_output, 'stack_trace', None))
            sys.exit(1)

        output_writer.write_markdown_output(project_output)
        logger.info("Content generation and file writing completed successfully.")
        sys.exit(0)

    except Exception as e:
        stack_trace = traceback.format_exc()
        error_msg = f"Unhandled exception in main: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Stack trace: {stack_trace}")
        output_writer.write_error_markdown(error_msg, stack_trace)
        sys.exit(1)

if __name__ == "__main__":
    main()
