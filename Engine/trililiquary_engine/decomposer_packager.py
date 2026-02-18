# decomposer_packager.py

"""
One-click backup and recovery utility for the Decomposer assistant.

Includes:
✅ Assistant config snapshot
✅ Assistant recreate logic (via OpenAI API)
✅ File reattachment logic
✅ .env patching
✅ JSON format validation runner
"""

import os
import json
import time
from pathlib import Path
from openai import OpenAI
from dotenv import dotenv_values, set_key

SECRETS_PATH = Path("secrets/decomposer.env")
BACKUP_DIR = Path("backups")
CONFIG_FILE = BACKUP_DIR / "decomposer_config.json"
ARC_DOC = Path("docs/The 7 Rhetorical Arcs.docx")

BACKUP_DIR.mkdir(exist_ok=True)


def load_env():
    config = dotenv_values(SECRETS_PATH)
    return config["OPENAI_API_KEY"], config.get("DECOMPOSER_ID")


def snapshot_assistant(api_key, assistant_id):
    client = OpenAI(api_key=api_key)
    assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
    with open(CONFIG_FILE, "w") as f:
        json.dump(assistant.model_dump(), f, indent=2)
    print("✅ Assistant snapshot saved to", CONFIG_FILE)


def recreate_assistant(api_key):
    client = OpenAI(api_key=api_key)

    file = client.files.create(
        file=open(ARC_DOC, "rb"),
        purpose="assistants"
    )
    print("📎 Uploaded rhetorical arcs doc:", file.id)

    instructions = (
        "You are a deterministic rhetorical decomposition engine. "
        "Use the attached 7 Rhetorical Arcs document. "
        "Output JSON with 7 fields: Essence, Form, Function, Context, Intent, Relation, Value. "
        "No commentary. If undeterminable, return null."
    )

    assistant = client.beta.assistants.create(
        name="Decomposer",
        model="gpt-4o",
        instructions=instructions,
        file_ids=[file.id],
        tools=[{"type": "file_search"}]
    )

    print("✅ Recreated assistant:", assistant.id)
    set_key(str(SECRETS_PATH), "DECOMPOSER_ID", assistant.id)
    return assistant.id


def validate_output_format(sample_response):
    try:
        obj = json.loads(sample_response)
        required = ["Essence", "Form", "Function", "Context", "Intent", "Relation", "Value"]
        for key in required:
            if key not in obj:
                raise ValueError(f"Missing field: {key}")
        print("✅ Valid rhetorical arc JSON.")
    except Exception as e:
        print("❌ Validation failed:", e)


if __name__ == "__main__":
    api_key, existing_id = load_env()

    if existing_id:
        snapshot_assistant(api_key, existing_id)
    else:
        print("⚠️ No existing assistant ID found. Creating a new one...")

    new_id = recreate_assistant(api_key)
    print("🧠 Decomposer is ready:", new_id)

    # (Optional) Add test case
    # response = "{"Essence": "Tool", ... }"
    # validate_output_format(response)
