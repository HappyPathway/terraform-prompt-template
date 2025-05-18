currently we're only outputting one file and it's a combination of project prompt and copilot-instructions.

I wanna split the outputs of this terraform module, we should have an output for project prompt (everything that's not the copilot-instructions.md file content) and one for copilot-instructions.md.

For the copilot-instructions.md we should take the output for the project prompt and re-submit back to a Gemini Pydantic AI Agent 
and ask it to research proper instructions for copilot. 

copilot-instructions.md: https://code.visualstudio.com/docs/copilot/copilot-customization

prompt file: https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files-experimental

Workspace prompt files: are only available within the workspace and are stored in the .github/prompts folder of the workspace.

should be called .github/prompts/project-prompt.md

we will not output a README.md file as we want the README.md to be specific to the project and not part of the context seed for Agentic coding.
Does this make sense?