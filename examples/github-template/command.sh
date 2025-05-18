python ../../gemini_generator.py \
     --project_prompt "    Create a Python based app for analyzing trade and investment data.
    It should able to output PDF reports and email them to subscribers.
    It should be able to run in Github Actions as a cron job and should fetch data from
    publicly available APIs and databases. It should use Pydantic and PydanticAI to 
    query Gemini and Google Search for data and information. 
    It should able to predict patterns. Track history of investment predictions and grade itself.
    Part of the daily report should include it's previous prediction and rating on accuracy.
    We will need to use multiple models and agents working in concert to achieve this.
    We will want to leverage SQLAlchemy and SQLite to store the data, we will want to 
    push and pull this data from GCS.
" \
     --repo_org "HappyPathway" \
     --project_name "smart-invest" \
     --gemini_model "gemini-2.5-pro-preview-05-06" \
     --json_output "./templates/python-github-actions-template.json" \
     --markdown_output "./templates/python-github-actions-template.md" \
     --project_prompt_output "../../project-prompt.md" \
     --copilot_instructions_output "../../copilot-instructions.md" \
     --github_project_prompt_output ".github/prompts/project-prompt.md" \
     --enable_search_grounding "true" \
     --placeholder_format "{{%s}}" \
     --placeholder_vars "project_name,repo_org,project_type,programming_language" \
     --temperature 0.2 \
     --top_p 0.95 \
     --top_k 40 \
     --max_output_tokens 32768
