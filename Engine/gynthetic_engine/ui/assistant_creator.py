# assistant_creator.py

from openai import OpenAI
from dotenv import set_key
from pathlib import Path

SECRETS_DIR = Path("secrets")
SECRETS_DIR.mkdir(exist_ok=True)

def create_and_save_assistant(api_key: str, role: str, name: str, prompt: str) -> str:
    client = OpenAI(api_key=api_key)

    assistant = client.beta.assistants.create(
        name=name.strip() or f"{role.capitalize()}Assistant",
        instructions=prompt.strip(),
        model="gpt-4o",
        tools=[]
    )

    # Save to secrets/decomposer.env or secrets/composer.env
    env_path = SECRETS_DIR / f"{role}.env"
    set_key(env_path, "OPENAI_API_KEY", api_key)
    set_key(env_path, f"{role.upper()}_ID", assistant.id)
    set_key(env_path, f"{role.upper()}_NAME", name.strip())

    print(f"✅ Created {role} assistant: {name} → {assistant.id}")
    return assistant.id
