#!/usr/bin/env python3
"""
Simple test script to verify the --output_dir functionality in gemini_generator.py
"""
import os
import sys
import argparse
import shutil
from pathlib import Path

# Mock argparse.Namespace object with required attributes
class MockArgs:
    def __init__(self, output_dir=None, preserve_relative_paths=False):
        # Define various output paths with different directory structures
        self.json_output = "templates/output.json"
        self.markdown_output = "docs/output.md"
        self.project_prompt_output = "project-prompt.md"
        self.github_project_prompt_output = ".github/prompts/project-prompt.md"
        self.copilot_instructions_output = "docs/github/copilot-instructions.md"
        self.output_dir = output_dir
        self.preserve_relative_paths = preserve_relative_pathson3
"""
Simple test script to verify the --output_dir functionality in gemini_generator.py
"""
import os
import sys
import argparse
import shutil
from pathlib import Path

# Mock argparse.Namespace object with required attributes
class MockArgs:
    def __init__(self, output_dir=None):
        self.json_output = "output.json"
        self.markdown_output = "output.md"
        self.project_prompt_output = "project-prompt.md"
        self.github_project_prompt_output = ".github/prompts/project-prompt.md"
        self.copilot_instructions_output = "copilot-instructions.md"
        # Add more complex paths to test directory preservation
        self.complex_path_1 = "deeply/nested/directory/structure/file.md"
        self.complex_path_2 = "/absolute/path/to/some/file.json"
        self.complex_path_3 = "../relative/path/file.txt"
        self.output_dir = output_dir

# Create a mock Template class for testing
class MockTemplate:
    def render(self, data):
        return "Mock template rendering"

# Test scenarios
def run_tests():
    # Import the OutputFileWriter class from gemini_generator
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from gemini_generator import OutputFileWriter
    except ImportError:
        print("Error: Could not import OutputFileWriter from gemini_generator.py")
        sys.exit(1)

    # Test directories
    test_dir = Path("./test_output_dir_results")
    
    # Clean up any previous test results
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create test directory
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Without output_dir
    print("\n--- Test 1: Without output_dir ---")
    args = MockArgs()
    writer = OutputFileWriter(args, MockTemplate())
    
    # Test 2: With output_dir
    print("\n--- Test 2: With output_dir ---")
    output_dir = test_dir / "all_outputs"
    args_with_dir = MockArgs(output_dir=str(output_dir))
    writer_with_dir = OutputFileWriter(args_with_dir, MockTemplate())
    
    # Test _write_file method with output_dir
    print("\nTesting _write_file with output_dir")
    writer_with_dir._write_file('json_output', '{"test": "content"}', "Failed to write test JSON")
    writer_with_dir._write_file('markdown_output', '# Test Markdown', "Failed to write test Markdown")
    writer_with_dir._write_file('project_prompt_output', '# Test Project Prompt', "Failed to write test project prompt")
    writer_with_dir._write_file('github_project_prompt_output', '# Test GitHub Project Prompt', "Failed to write test GitHub project prompt")
    writer_with_dir._write_file('copilot_instructions_output', '# Test Copilot Instructions', "Failed to write test Copilot instructions")
    
    # Clean up the output directory and test again with realistic paths
    print("\nTesting with realistic paths from logs")
    shutil.rmtree(output_dir)
    
    realistic_args = MockArgs(output_dir=str(output_dir))
    realistic_args.json_output = "./templates/python-github-actions-template.json"
    realistic_args.markdown_output = "./templates/python-github-actions-template.md"
    realistic_args.project_prompt_output = "../../project-prompt.md"
    realistic_args.github_project_prompt_output = ".github/prompts/project-prompt.md"
    realistic_args.copilot_instructions_output = "../../copilot-instructions.md"
    
    realistic_writer = OutputFileWriter(realistic_args, MockTemplate())
    
    print("\nTesting _write_file with realistic paths")
    realistic_writer._write_file('json_output', '{"test": "realistic content"}', "Failed to write test JSON")
    realistic_writer._write_file('markdown_output', '# Test Realistic Markdown', "Failed to write test Markdown")
    realistic_writer._write_file('project_prompt_output', '# Test Realistic Project Prompt', "Failed to write test project prompt")
    realistic_writer._write_file('github_project_prompt_output', '# Test Realistic GitHub Project Prompt', "Failed to write test GitHub project prompt") 
    realistic_writer._write_file('copilot_instructions_output', '# Test Realistic Copilot Instructions', "Failed to write test Copilot instructions")
    
    # Verify the files were created in the output directory
    print("\nVerifying files in output directory:")
    if output_dir.exists():
        print(f"Output directory created: {output_dir}")
        
        # Recursively list all files with their paths
        def list_files(directory, indent=0):
            for path in sorted(directory.iterdir()):
                if path.is_file():
                    print(f"{' ' * indent}- {path.relative_to(output_dir)}")
                elif path.is_dir():
                    print(f"{' ' * indent}+ {path.name}/")
                    list_files(path, indent + 2)
        
        list_files(output_dir)
    else:
        print(f"ERROR: Output directory was not created: {output_dir}")

if __name__ == "__main__":
    run_tests()
