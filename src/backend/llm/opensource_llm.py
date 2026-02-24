"""
Open Source LLM Interface
Supports local models via Ollama - completely free and private
"""
import requests
import json
import time
import httpx
from typing import Optional, List, Dict, Any
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class OllamaLLM:
    """
    Local LLM interface using Ollama
    Completely free, private, and open source
    """
    
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            model: Model name (e.g., "llama3.2:3b", "mistral:7b", "codellama:7b")
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.conversation_history = []
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Connected to Ollama server")
                return True
            else:
                logger.warning(f"⚠️ Ollama server returned {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Cannot connect to Ollama: {e}")
            logger.info("💡 Make sure Ollama is installed and running: ollama serve")
            return False
    
    def pull_model(self, model: Optional[str] = None) -> bool:
        """
        Pull/download a model if not available locally
        
        Args:
            model: Model name to pull (uses self.model if None)
            
        Returns:
            True if successful
        """
        model_name = model or self.model
        
        try:
            logger.info(f"📥 Pulling model: {model_name}")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                # Parse streaming response for progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'status' in data:
                                print(f"\r{data['status']}", end='', flush=True)
                        except:
                            pass
                
                print("\n✅ Model pulled successfully!")
                return True
            else:
                logger.error(f"❌ Failed to pull model: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model pull failed: {e}")
            return False
    
    def list_models(self) -> List[Dict]:
        """List available local models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except:
            return []
    
    def is_model_available(self, model: Optional[str] = None) -> bool:
        """Check if model is available locally"""
        model_name = model or self.model
        models = self.list_models()
        
        for model_info in models:
            if model_info.get('name', '').startswith(model_name):
                return True
        
        return False
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        use_smart_prompting: bool = False,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for randomness (0.0-2.0)
            system_prompt: System instructions
            stream: Whether to stream response
            
        Returns:
            Generated text
        """
        try:
            # Ensure model is available
            if not self.is_model_available():
                logger.warning(f"Model {self.model} not found locally. Attempting to pull...")
                if not self.pull_model():
                    return "❌ Model not available and could not be downloaded"
            
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history (last 6 messages for context)
            for msg in self.conversation_history[-6:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_ctx": 4096,  # Context window
                    "num_predict": min(max_tokens, 1024)  # Limit for speed
                }
            }
            
            logger.info(f"🤖 Generating with {self.model}...")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'message' in data and 'content' in data['message']:
                                    full_response += data['message']['content']
                            except:
                                continue
                    result = full_response
                else:
                    # Handle regular response
                    data = response.json()
                    result = data.get('message', {}).get('content', 'No response generated')
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": result})
                
                logger.info(f"✅ Generated {len(result)} characters")
                return result
                
            else:
                logger.error(f"❌ Ollama generation failed: {response.status_code}")
                return f"❌ Generation failed: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return f"❌ Error: {str(e)}"
    
    def reset_history(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_info(self) -> Dict[str, Any]:
        """Get Ollama setup information"""
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
            "available_models": [m.get('name', '') for m in self.list_models()],
            "model_ready": self.is_model_available(),
            "server_running": self._test_connection(),
            "open_source": True,
            "offline": True,
            "cost": "Free"
        }

class OpenSourceLLMInterface:
    """
    Unified interface for open source LLMs
    Handles multiple local LLM providers with automatic fallbacks
    """
    
    def __init__(self, provider: str = "ollama", model: str = "llama3.2:3b"):
        """
        Initialize open source LLM interface
        
        Args:
            provider: LLM provider (ollama, huggingface, ...)
            model: Model name
        """
        self.provider = provider
        self.model = model
        self.llm_client = None
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM client with fallbacks"""
        try:
            if self.provider == "ollama":
                self.llm_client = OllamaLLM(model=self.model)
                logger.info(f"✅ Ollama LLM initialized: {self.model}")
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.warning(f"❌ Primary LLM ({self.provider}) failed: {e}")
            
            # Try Hugging Face fallback
            try:
                logger.info("🔄 Trying Hugging Face Transformers fallback...")
                from backend.llm.huggingface_llm import LocalLLMFallback
                self.llm_client = LocalLLMFallback()
                self.provider = "huggingface"
                logger.info("✅ Hugging Face LLM fallback initialized")
            except Exception as e2:
                logger.error(f"❌ All LLM options failed: {e2}")
                raise RuntimeError("No LLM could be initialized")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text with the configured LLM"""
        if not self.llm_client:
            return "❌ LLM not initialized"
        
        return self.llm_client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs
        )
    
    def get_setup_info(self) -> Dict[str, Any]:
        """Get setup and configuration info"""
        if self.llm_client:
            info = self.llm_client.get_info()
            info_dict: Dict[str, Any] = {
                "provider": self.provider,
                "model": self.model,
                "open_source": True,
                "status": "Ready"
            }
            info.update(info_dict)
            return info
        
        return {
            "provider": self.provider,
            "model": self.model,
            "status": "Not initialized",
            "open_source": True
        }

    async def generate_async(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        """
        Async streaming generator for local Ollama-based LLMs.
        Yields content chunks as they arrive from the Ollama server.
        """
        if not self.llm_client:
            yield "❌ LLM not initialized"
            return

        # Check if this is a LocalLLMFallback (no streaming support)
        from backend.llm.huggingface_llm import LocalLLMFallback
        if isinstance(self.llm_client, LocalLLMFallback):
            # Fallback to synchronous generation for LocalLLMFallback
            try:
                import asyncio
                response = self.llm_client.generate(prompt, max_tokens, temperature, system_prompt)
                # Chunk the response
                chunk_size = 50
                for i in range(0, len(response), chunk_size):
                    chunk = response[i:i+chunk_size]
                    yield chunk
                    await asyncio.sleep(0.05)  # Small delay for streaming effect
            except Exception as e:
                yield f"❌ Local LLM error: {str(e)}"
            return

        # Regular Ollama streaming
        url = f"{self.llm_client.base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if hasattr(self.llm_client, 'conversation_history') and self.llm_client.conversation_history:
            for msg in self.llm_client.conversation_history[-6:]:
                messages.append(msg)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.llm_client.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
                "num_predict": min(max_tokens, 1024),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload) as resp:
                    if resp.status_code != 200:
                        err = await resp.aread()
                        yield f"❌ Ollama error: {resp.status_code}"
                        return

                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            # Ollama streaming uses 'message' with 'content'
                            content = data.get('message', {}).get('content')
                            if content:
                                yield content
                        except Exception:
                            # ignore non-json lines
                            continue

        except Exception as e:
            yield f"❌ Streaming error: {e}"
            return