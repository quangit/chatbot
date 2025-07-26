# Copilot Instructions for AI Coding Agents

## Project Overview
This project is a Python-based chatbot. The codebase structure and conventions are designed for clarity and extensibility. There is no monolithic entrypoint or explicit build/test workflow detected yet—review and update this file as the project evolves.

## Key Architectural Patterns
- **Component Structure:** Organize code by feature or service. Each major capability should have its own module or directory.
- **Model Switching:** The chatbot supports switching between different AI models (e.g., GPT-3.5, GPT-4) by changing the model name in the configuration or code. Example:
  ```python
  response = openai.ChatCompletion.create(
      model="gpt-4",  # Change to desired model
      messages=messages
  )
  ```
- **Configuration:** Store secrets and model settings in environment variables or a config file. Avoid hardcoding sensitive values.

## Developer Workflows
- **Run the chatbot:** Use the main Python script (e.g., `python main.py`) or the appropriate entrypoint for your framework.
- **Dependencies:** Use `requirements.txt` or `pyproject.toml` for dependency management. Install with `pip install -r requirements.txt` if present.
- **Testing:** If tests exist, they should be in a `tests/` directory or follow the `test_*.py` naming convention. Run with `pytest` or `python -m unittest`.

## Project-Specific Conventions
- **Model Selection:** Always make model selection explicit in code or config. Document supported models in the README or config comments.
- **Extensibility:** Add new features as separate modules. Follow existing import and structure patterns.
- **Environment Variables:** Use `.env` or OS environment variables for API keys and configuration.

## Integration Points
- **External APIs:** The chatbot likely integrates with OpenAI or similar services. Ensure API keys are managed securely.
- **Configuration Files:** Look for `.env`, `config.py`, or similar for runtime settings.

## Example: Switching Models
```python
# ...existing code...
response = openai.ChatCompletion.create(
    model="gpt-4",  # Change this to switch models
    messages=messages
)
# ...existing code...
```

## Key Files & Directories
- `main.py` (or similar): Entrypoint for running the chatbot
- `requirements.txt` / `pyproject.toml`: Dependency management
- `tests/`: (If present) Automated tests
- `.env` / `config.py`: Configuration and secrets

---

_If any conventions or workflows are unclear or missing, please provide feedback to improve these instructions._
