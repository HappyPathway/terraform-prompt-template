#!/usr/bin/env python3
"""
Test script to verify that errors are properly propagated and the program exits early.
"""
import os
import sys
import subprocess
import time

def run_test():
    """Run a test with deliberately invalid API key to trigger failure"""
    print("Testing error handling in gemini_generator.py...")
    
    # Save current environment
    original_env = os.environ.copy()
    
    try:
        # Set invalid API key to force error
        os.environ["GEMINI_API_KEY"] = "INVALID_KEY_FOR_TESTING"
        
        # Create a temporary output directory
        test_output_dir = "test_error_handling_output"
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Define command arguments for a minimal test
        cmd = [
            "python",
            "gemini_generator.py",
            "--project_name", "Test Error Handling",
            "--project_prompt", "This is a test prompt that will fail.",
            "--repo_org", "test-org",
            "--json_output", f"{test_output_dir}/output.json",
            "--markdown_output", f"{test_output_dir}/output.md",
            "--output_dir", test_output_dir
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Execute the command and capture output
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            
            print(f"Process exited with code: {result.returncode}")
            print(f"Process runtime: {end_time - start_time:.2f} seconds")
            print("\nSTDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            
            # Check if the process exited with an error code as expected
            if result.returncode != 0:
                print("✅ Test passed: Process exited with non-zero error code as expected")
            else:
                print("❌ Test failed: Process exited with zero code, which means it didn't detect the error correctly")
            
            # Check if error output files were created
            json_path = os.path.join(test_output_dir, "output.json")
            md_path = os.path.join(test_output_dir, "output.md")
            
            # Search for output files if they're not in the expected location
            if not os.path.exists(json_path):
                print(f"File not found at expected path: {json_path}")
                # Try to find the file
                for root, _, files in os.walk(test_output_dir):
                    for file in files:
                        if file.endswith('.json'):
                            json_path = os.path.join(root, file)
                            print(f"Found JSON file at: {json_path}")
                            break
            
            if not os.path.exists(md_path):
                print(f"File not found at expected path: {md_path}")
                # Try to find the file
                for root, _, files in os.walk(test_output_dir):
                    for file in files:
                        if file.endswith('.md'):
                            md_path = os.path.join(root, file)
                            print(f"Found Markdown file at: {md_path}")
                            break
            
            # Check JSON file
            if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                file_size = os.path.getsize(json_path)
                print(f"✅ JSON error output file created: {json_path} ({file_size} bytes)")
                # Optionally check content
                with open(json_path, 'r') as f:
                    content = f.read()
                    if '"error":' in content:
                        print("✅ Error field found in JSON output")
                    else:
                        print("❌ No error field found in JSON output")
            else:
                print(f"❌ JSON error output file not created or empty: {json_path}")
            
            # Check Markdown file
            if os.path.exists(md_path) and os.path.getsize(md_path) > 0:
                file_size = os.path.getsize(md_path)
                print(f"✅ Markdown error output file created: {md_path} ({file_size} bytes)")
                with open(md_path, 'r') as f:
                    content = f.read()
                    if 'Error' in content:
                        print("✅ Error message found in Markdown output")
                    else:
                        print("❌ No error message found in Markdown output")
            else:
                print(f"❌ Markdown error output file not created or empty: {md_path}")
                
        except subprocess.SubprocessError as e:
            print(f"Failed to run test: {e}")
    
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

if __name__ == "__main__":
    run_test()
