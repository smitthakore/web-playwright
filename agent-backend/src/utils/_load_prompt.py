from pathlib import Path
from typing import Optional
import json


def load_prompt(category: Optional[str], name: str) -> str:
    """
    Load a prompt file from the agent-backend/prompts directory.
    Args:
        category: prompt category (or None/empty to skip category)
        name: prompt filename (with or without extension) or relative path

    Returns:
        Prompt content as a string (trimmed)
    """
    # Resolve repo root (agent-backend is two levels up from this file)
    repo_root = Path(__file__).resolve().parents[2]
    prompts_dir = repo_root / "prompts"

    candidate_paths = []

    # If caller passed an explicit path in `name`, prefer it
    explicit = Path(name)
    if explicit.exists():
        prompt_path = explicit
    else:
        # Try category-based path first (if provided)
        if category:
            candidate_paths.append(prompts_dir / category / f"{name}.md")
            candidate_paths.append(prompts_dir / category / name)

        # Try root prompts directory
        candidate_paths.append(prompts_dir / f"{name}.md")
        candidate_paths.append(prompts_dir / name)

        # Pick the first existing candidate
        prompt_path = None
        for p in candidate_paths:
            if p.exists():
                prompt_path = p
                break

    if prompt_path is None or not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found. Checked: {', '.join(str(p) for p in candidate_paths)}")

    return prompt_path.read_text(encoding="utf-8")
