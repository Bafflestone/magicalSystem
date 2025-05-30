import ollama
from dotenv import load_dotenv
from config import use_local_llm, ollama_llm, openai_llm
from typing import Any, Optional
from openai import OpenAI

load_dotenv()
client = OpenAI()

def call_llm(prompt: str, output_format: Optional[Any] = None) -> str:
    """Call the LLM API with a prompt."""
    if use_local_llm:
        return call_ollama(prompt, output_format)
    else:
        return call_openai(prompt, output_format)

def call_ollama(prompt: str, output_format: Any, llm: str = ollama_llm) -> str:
    """Call the local Ollama API with a prompt."""
    print("calling ollama")
    if output_format:
        print("main output format.")
        response = ollama.chat(
            model=llm,
            format=output_format.model_json_schema(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return output_format.model_validate_json(response.message.content)
    else:
        response = ollama.chat(
            model=llm,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.message.content


def call_openai(prompt: str, output_format: Any, llm: str = openai_llm) -> str:
    """Call the OpenAI API with a prompt."""
    print("calling openai")
    if output_format:
        response = client.responses.parse(
            model=llm,
            input=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            text_format=output_format,
        )
        return response.output_parsed
    else:
        response = client.responses.parse(
            model=llm,
            input=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response.output_parsed