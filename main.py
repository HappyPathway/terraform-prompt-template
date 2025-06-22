# Importing modules
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
    def __init__(self, api_key: str, enable_search_grounding: bool = True):
        self.enable_search_grounding = enable_search_grounding
        self.api_key = api_key
        self.available_models = None

    def configure_api(self, api_key: str) -> bool:
        try:
            genai.configure(api_key=api_key, transport='rest')
            return True
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            return False
    
    def create_pydantic_agent(self, model_name: str, token_config: Dict,
                              deps_type: Type[BaseModel], output_type: Type[BaseModel],
                              system_prompt_str: str,
                              context_template_str: Optional[str] = None,
                              context_data_func: Optional[Callable[[RunContext], Dict[str, Any]]] = None) -> Agent:
        logger.info(f"Creating Pydantic agent with model {model_name}")
        
        google_search = None
        if self.enable_search_grounding:
            try:
                google_search = Tool(function=GoogleSearch(), name="web_search")
            except Exception as e:
                logger.warning(f"Failed to enable Google Search grounding: {e}")

        # Create a Gemini model instance
        try:
            gemini_model = genai.GenerativeModel(model_name=model_name)
            logger.info(f"Successfully created Gemini model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {e}")
            raise RuntimeError(f"Failed to create Gemini model. Error: {e}")
            
        content_agent = Agent(
            model=gemini_model,  # Set the model directly on the agent
            model_settings=GeminiModelSettings(
                model_name=model_name,
                api_key=self.api_key,
                tools=[google_search] if google_search else None,
                **token_config,
            ),
            dependencies=deps_type,
            output_type=output_type,
            system_prompt=system_prompt_str, 
            output_parser=ModelRetry(3),  # Retry up to 3 times on output parsing errors
        )

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
    suggested extensions and documentation sources using a Gemini agent.
    """
    def __init__(self, common_tools: CommonGeminiTools, project_name: str, project_prompt_text: str,
                 repo_org: str, model_name: str, token_config: Dict[str, Any]):
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
        try:
            def project_context_data_func(ctx: RunContext[ProjectInfo]) -> Dict[str, Any]:
                    # Access context dependencies - they should never be None when this function is called
                # during the actual execution
                return {
                    "project_name": ctx.deps.project_name if ctx.deps else self.project_name,
                    "repo_org": ctx.deps.repo_org if ctx.deps else self.repo_org,
                    "project_prompt": ctx.deps.project_prompt if ctx.deps else self.project_prompt_text,
                }

            content_agent = self.common_tools.create_pydantic_agent(
                model_name=self.model_name,
                token_config=self.token_config,
                deps_type=ProjectInfo,
                output_type=ProjectOutput,
                system_prompt_str=self.system_prompt_template_str,
                context_template_str=self.context_template_str,
                context_data_func=project_context_data_func
            )

            # Try without the model parameter since model_settings is already configured in the agent
            return content_agent.run_sync(
                ProjectInfo(
                    project_name=self.project_name,
                    repo_org=self.repo_org,
                    project_prompt=self.project_prompt_text
                )
            )

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
    def __init__(self, args, main_markdown_template):
        self.args = args
        self.main_markdown_template = main_markdown_template

    def write_markdown_output(self, project_output: ProjectOutput):
        """Writes markdown output to either specified path or default location."""
        output_content = project_output.readme_content

        # Use output_dir path if specified
        if hasattr(self.args, 'output_dir') and self.args.output_dir:
            output_path = os.path.join(
                self.args.output_dir,
                os.path.basename(self.args.markdown_output)
            )
        else:
            output_path = self.args.markdown_output

        logger.info(f"Writing markdown output to {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)

    def write_error_markdown(self, error_msg: str, stack_trace: Optional[str] = None):
        """Writes error information to the markdown output file."""
        error_content = f"# Error During Generation\n\n{error_msg}"
        if stack_trace:
            error_content += f"\n\n## Stack Trace\n\n```\n{stack_trace}\n```"
        
        if hasattr(self.args, 'output_dir') and self.args.output_dir:
            error_path = os.path.join(
                self.args.output_dir,
                os.path.basename(self.args.markdown_output)
            )
        else:
            error_path = self.args.markdown_output

        logger.info(f"Writing error markdown to {error_path}")
        os.makedirs(os.path.dirname(error_path), exist_ok=True)
        
        with open(error_path, 'w', encoding='utf-8') as f:
            f.write(error_content)

class ProjectPrompt:
    """
    Encapsulates the project content generation workflow, including main content,
    project prompts and copilot instructions.
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
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{error_msg}\n{stack_trace}")
        output_writer.write_error_markdown(error_msg, stack_trace)
        sys.exit(1)

if __name__ == "__main__":
    main()
