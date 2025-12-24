def extract_python_code(content: str) -> str:
    """
    Extract Python code from an LLM response.

    Handles fenced and unfenced code blocks.
    """
    if "```python" in content:
        return content.split("```python")[1].split("```")[0].strip()

    if "```" in content:
        return content.split("```")[1].split("```")[0].strip()

    return content.strip()
