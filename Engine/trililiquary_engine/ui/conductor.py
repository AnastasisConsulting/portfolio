import os
import openai
from dotenv import load_dotenv

# === Load API keys and identifiers === #
load_dotenv("conductor.env")  # Make sure this file is in the project root or adjust path

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CONDUCTOR_ID = os.getenv("CONDUCTOR_ID")
CONDUCTOR_NAME = os.getenv("CONDUCTOR_NAME")

openai.api_key = OPENAI_API_KEY

# === Core Conductor Inference Function === #
def send_to_conductor(ranked_arcs, mini_prompts, template_type="default", temperature=1.0):
    """
    Sends 7 resolved arc mini-prompts to the Conductor LLM for final synthesis.

    Args:
        ranked_arcs (List[str]): Arc names in priority order (e.g. ["essence", ...])
        mini_prompts (List[str]): Resolved mini-prompts for each arc
        template_type (str): Domain-specific tone hint (e.g., "narrative", "academic")
        temperature (float): OpenAI completion temperature

    Returns:
        str: Final synthesized output from the Conductor
    """
    if len(ranked_arcs) != 7 or len(mini_prompts) != 7:
        raise ValueError("Conductor expects exactly 7 arcs and 7 mini-prompts.")

    system_prompt = (
        "You are the Conductor Agent.\n"
        "You receive a ranked list of 7 rhetorical arcs. Each arc has been cognitively transformed\n"
        "across three phases and resolved into a mini-prompt.\n"
        "Your task is to weave these into a unified, expressive final output.\n"
        "Do not list the arcs. Do not explain your reasoning. Just compose.\n"
        f"Output style: {template_type}"
    )

    user_prompt = "\n".join([
        f"{i+1}. [{arc}] {mini}" for i, (arc, mini) in enumerate(zip(ranked_arcs, mini_prompts))
    ])

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )

    return response["choices"][0]["message"]["content"].strip()

# === Optional: Token Logging === #
def log_conductor_usage(response):
    """
    Logs token usage from the OpenAI response object.
    """
    usage = response.get("usage", {})
    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    total = usage.get("total_tokens", 0)
    print(f"[Conductor] Tokens used — Prompt: {prompt}, Completion: {completion}, Total: {total}")
    return usage
