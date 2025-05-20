python ../../gemini_generator.py \
     --project_prompt "Develop a comprehensive personal wellness and productivity hub. Core functionalities include:
-   **Exercise Logging:** Track diverse physical activities, monitor progress, and integrate with wearables.
-   **Nutrition Management:** Log meals, analyze nutritional intake (calories, macros), and access a food database.
-   **Personalized Coaching:** Offer insights, goal setting, and progress reports based on user data.
Additional desirable features: water intake, sleep tracking, mindfulness exercises, and recipe suggestions.
Prioritize a user-friendly interface, robust data security, and cross-platform compatibility.
The backend should be Python-based, and the app should be designed for scalability and easy maintenance." \
     --repo_org "HappyPathway" \
     --project_name "smart-wise" \
     --gemini_model "gemini-2.5-pro-preview-05-06" \
     --markdown_output "./templates/python-github-actions-template.md" \
     --enable_search_grounding "true" \
     --placeholder_format "{{%s}}" \
     --placeholder_vars "project_name,repo_org,project_type,programming_language" \
     --temperature 0.2 \
     --top_p 0.95 \
     --top_k 40 \
     --max_output_tokens 32768 \
     --markdown_output "docs/output.md" \
     --output_dir "${PWD}/templates"
