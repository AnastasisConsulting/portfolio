# llm_helpers/openai_interface.py (unified)

from openai import OpenAI
from dotenv import dotenv_values
from pathlib import Path
import os
import time


def load_env(env_path: Path) -> dict:
    config = dotenv_values(env_path)

    print(f"🧪 Loading .env from: {env_path}")
    print(f"📦 Contents: {config}")

    api_key = config.get("OPENAI_API_KEY")
    assistant_id = (
        config.get("ASSISTANT_ID") or
        config.get("DECOMPOSER_ID") or
        config.get("COMPOSER_ID")
    )
    if not api_key or not assistant_id:
        raise ValueError(f"Missing API key or assistant ID in {env_path}")
    return {"api_key": api_key, "assistant_id": assistant_id}


def ping_assistant(env_path: Path) -> str:
    creds = load_env(env_path)
    print(f"📤 [PING] Assistant ID: {creds['assistant_id']}")

    client = OpenAI(api_key=creds["api_key"])

    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello assistant, who are you?"
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=creds["assistant_id"]
        )

        while run.status not in ("completed", "failed", "cancelled"):
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status != "completed":
            return f"❌ Assistant run failed with status: {run.status}"

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return f"👤 Assistant ID: {creds['assistant_id']}\n💬 Reply: {messages.data[0].content[0].text.value}"

    except Exception as e:
        return f"❌ Ping failed: {e}"


def send_message_to_assistant(env_path: Path, user_input: str) -> str:
    creds = load_env(env_path)
    print(f"📤 [SEND] Assistant ID: {creds['assistant_id']}")

    client = OpenAI(api_key=creds["api_key"])

    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=creds["assistant_id"]
        )

        start = time.time()
        while run.status not in ("completed", "failed", "cancelled"):
            if time.time() - start > 30:
                raise TimeoutError("Assistant response timed out.")
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status != "completed":
            return f"❌ Run failed with status: {run.status}"

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value

    except Exception as e:
        return f"❌ Error: {e}"
