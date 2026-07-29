import json
from llama_cpp import Llama

class CharacterBrain:
    def __init__(self, model_path: str):
        self.llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=4096)

    def load_profile(self, filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def generate_from_prompt(self, full_prompt: str, temperature: float = 0.7) -> str:
        reply = self.llm(
            full_prompt,
            max_tokens=512, # Capped safely
            temperature=temperature,
            stop=[
                "\nUser:", "User:", "\nSystem:", "System:", "\nAdmin:", "Admin:", 
                "<|eot_id|>", "<|end_of_text|>", "<|im_end|>"
            ]
        )["choices"][0]["text"].strip()
        
        return reply