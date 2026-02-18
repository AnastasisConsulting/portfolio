# Auto-generated placeholder
import os
import json
import openai
from typing import List, Dict, Optional

# --- Output System Prompt ---
SYSTEM_PROMPT = """
You are a synthesis engine. You are given a prompt stack composed of multiple rhetorical fragments.
Your job is to weave these into a coherent, structured natural language output.
Do not inject new logic. Do not rearrange the prompt order.
Your synthesis must respect the arc sequence exactly as provided.
"""

def synthesize_output(
    prompt_stack: List[Dict[str, str]],
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    temperature: float = 0.3,
    top_p: float = 0.95,
    max_tokens: int = 750
) -> str:
    """
    Submits the final ordered triadic prompt stack to the output LLM.
    Returns the synthesized response as plain text.
    """
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenAI API key.")

    openai.api_key = api_key

    formatted_input = "\n\n".join(
        f"[{item['arc'].upper()}]\n{item['compiled_prompt']}" for item in prompt_stack
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatted_input}
        ],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )

    return response.choices[0].message["content"].strip()
