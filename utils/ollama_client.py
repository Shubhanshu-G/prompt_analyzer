"""Ollama LLM client for local model inference"""

import requests
from typing import List, Optional
import json
from config import OLLAMA_BASE_URL

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip('/')
        
    def list_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models  # Return full model names with tags
            return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def is_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False
    ) -> str:
        """Generate response from Ollama model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": stream,
                },
                timeout=300
            )
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    text = ""
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            text += chunk.get('response', '')
                    return text
                else:
                    data = response.json()
                    return data.get('response', '')
            else:
                return f"Error: Model returned status {response.status_code}"
        except requests.Timeout:
            return "Error: Request timed out. The model may be processing a long query."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_with_tokens(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> dict:
        """Generate response and return token count information"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": False,
                },
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get('response', ''),
                    "prompt_tokens": data.get('prompt_eval_count', self._estimate_tokens(prompt)),
                    "completion_tokens": data.get('eval_count', self._estimate_tokens(data.get('response', ''))),
                    "total_tokens": data.get('prompt_eval_count', 0) + data.get('eval_count', 0),
                    "model": model
                }
            else:
                return {
                    "response": f"Error: Model returned status {response.status_code}",
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "model": model
                }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "model": model
            }
    
    def generate_with_image(
        self,
        prompt: str,
        model: str,
        image_base64: str,
        temperature: float = 0.7
    ) -> dict:
        """Generate response using vision model with image input"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [image_base64],
                    "temperature": temperature,
                    "stream": False,
                },
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get('response', ''),
                    "prompt_tokens": data.get('prompt_eval_count', self._estimate_tokens(prompt)),
                    "completion_tokens": data.get('eval_count', self._estimate_tokens(data.get('response', ''))),
                    "total_tokens": data.get('prompt_eval_count', 0) + data.get('eval_count', 0),
                    "model": model
                }
            else:
                return {
                    "response": f"Error: Model returned status {response.status_code}",
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "model": model
                }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "model": model
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (1 token ≈ 4 characters)"""
        return len(text) // 4

