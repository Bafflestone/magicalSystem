import ollama
import json
import os
# Set Ollama host if running inside Docker
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

def call_ollama(prompt: str, model, llm: str = "qwen2.5:7b") -> str:
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