# Define Pydantic models for structured output
import json
import os
import sys
import logging
import time
from typing import Optional, List, Dict, Any

import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.gemini import GeminiModelSettings

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

class CopilotPromptContent(BaseModel):
    """Output model for Copilot instructions generation"""
    project_prompt_md: str = Field(description="GitHub project prompt content for .github/prompts/project-prompt.md")
    helpful_context: list[str] = Field(description="List of helpful contexts and resources for Copilot")
    project_specific_instructions: list[str] = Field(description="List of project-specific instructions for Copilot")

class CopilotAgentDeps(BaseModel):
    """Dependencies model for Copilot instructions agent"""
    project_name: str = Field(description="Name of the project")
    project_prompt: str = Field(description="Original project description")
    project_type: str = Field(description="Type of project")
    programming_language: str = Field(description="Primary programming language")
    best_practices: list[str] = Field(description="List of project best practices")
    documentation_sources: list[str] = Field(description="List of documentation sources")

class ProjectInfo(BaseModel):
    """Project context information for the agent"""
    project_name: str = Field(description="Name of the project")
    repo_org: str = Field(description="GitHub organization or username") 
    project_prompt: str = Field(description="Original project description")