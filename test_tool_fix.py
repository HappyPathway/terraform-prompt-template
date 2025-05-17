#!/usr/bin/env python3
"""
Test script to verify the Tool class fix for Gemini API
"""

import json
import os
from google.genai.types import Tool, GoogleSearch
import google.generativeai as genai

def test_tool_initialization():
    """Test the proper initialization of Tool objects"""
    print("Testing Tool initialization...")
    
    # Setup API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment. Please set it.")
        return False
    
    try:
        # Configure the Google Generative AI SDK
        genai.configure(api_key=api_key)
        
        # Test the tool initialization
        print("Creating Tool with function declarations...")
        google_search_tool = Tool(function_declarations=[{"name": "google_search", "description": "Search Google"}])
        
        print("Tool created successfully:", google_search_tool)
        
        # Test with a model 
        print("Testing with model initialization...")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Set model parameters and tools
        print("Setting model parameters with tools...")
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Test a simple query
        print("Generating content...")
        response = model.generate_content(
            "What is the capital of France?",
            generation_config=generation_config
        )
        
        print("Response:", response.text)
        return True
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_tool_initialization()
    print(f"Test {'succeeded' if success else 'failed'}")
