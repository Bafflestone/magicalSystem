import ollama
import json
from dotenv import load_dotenv
from config import use_local_llm, ollama_llm
from typing import Any

load_dotenv()

def call_llm(prompt: str, output_format: Any) -> str:
    """Call the local LLM API with a prompt."""
    if use_local_llm:
        return call_ollama(prompt, output_format)
    else:
        raise NotImplementedError("Remote LLM API not implemented.")

def call_ollama(prompt: str, model: Any, llm: str = ollama_llm) -> str:
    """Call the local Ollama API with a prompt."""
    response = ollama.chat(
        model=llm,
        format=model.model_json_schema(),
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content'].strip()


def extract_json(output: str) -> dict:
    """Extract and clean JSON from model output."""
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        start = output.find('{')
        end = output.rfind('}') + 1
        return json.loads(output[start:end])