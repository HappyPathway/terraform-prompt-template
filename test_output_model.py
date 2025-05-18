# A simple test script for ProjectOutput with error fields
from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectOutputTest(BaseModel):
    """Test version of ProjectOutput model"""
    readme_content: str = Field(description="Full README.md content")
    best_practices: list[str] = Field(description="List of 5-10 best practices") 
    suggested_extensions: list[str] = Field(description="List of recommended VS Code extensions")
    documentation_source: list[str] = Field(description="List of helpful documentation sources")
    copilot_instructions: str = Field(description="Instructions for GitHub Copilot")
    project_type: str = Field(description="The type of project")
    programming_language: str = Field(description="The primary programming language")
    error: Optional[str] = Field(default=None, description="Error message if content generation failed")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace for error debugging")

# Create a test instance with error fields
test_output = ProjectOutputTest(
    readme_content="Test content",
    best_practices=["Practice 1", "Practice 2"],
    suggested_extensions=["Extension 1", "Extension 2"],
    documentation_source=["Source 1", "Source 2"],
    copilot_instructions="Test instructions",
    project_type="Test Type",
    programming_language="Python",
    error="Test error message",
    stack_trace="Test stack trace"
)

# Print the model as a dict to verify all fields
print("Model dump:")
model_dict = test_output.model_dump()
for key, value in model_dict.items():
    print(f"{key}: {value}")

# Try creating JSON
import json
print("\nJSON output:")
json_output = json.dumps(model_dict, indent=2)
print(json_output)

# Create a model without error fields to ensure they're optional
test_output_no_error = ProjectOutputTest(
    readme_content="Test content",
    best_practices=["Practice 1", "Practice 2"],
    suggested_extensions=["Extension 1", "Extension 2"],
    documentation_source=["Source 1", "Source 2"],
    copilot_instructions="Test instructions",
    project_type="Test Type",
    programming_language="Python"
)

print("\nModel without error fields:")
no_error_dict = test_output_no_error.model_dump()
for key, value in no_error_dict.items():
    print(f"{key}: {value}")
