"""
Fallback Open Source LLM using Hugging Face Transformers
For when Ollama is not available
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional
import logging
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class HuggingFaceLLM:
    """
    Local LLM using Hugging Face Transformers
    Completely free and runs without external servers
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize Hugging Face model
        
        Args:
            model_name: HF model to use (smaller models for local use)
        """
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.generator = None
        self.conversation_history = []
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model and tokenizer"""
        try:
            logger.info(f"🤖 Loading {self.model_name} on {self.device}...")
            
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, padding_side='left')
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings for local use
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device.type == "cpu" and self.model is not None:
                self.model = self.model.to("cpu")  # type: ignore
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device.type == "cuda" else -1,
                trust_remote_code=True
            )
            
            logger.info(f"✅ {self.model_name} loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            # Fallback to a tiny model
            try:
                logger.info("Trying fallback to GPT-2...")
                self.model_name = "gpt2"
                self._load_gpt2_fallback()
            except Exception as e2:
                logger.error(f"❌ Fallback also failed: {e2}")
                raise
    
    def _load_gpt2_fallback(self):
        """Load GPT-2 as ultimate fallback"""
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained("gpt2")
        if self.model is not None:
            self.model = self.model.to("cpu")  # type: ignore
        
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device.type == "cuda" else -1
        )
        
        logger.info("✅ GPT-2 fallback loaded")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        use_smart_prompting: bool = False,
        **kwargs
    ) -> str:
        """Generate text using the local model"""
        try:
            # Prepare the input
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            else:
                full_prompt = f"User: {prompt}\nAssistant:"
            
            # Add conversation history for context
            if self.conversation_history:
                # Get last few exchanges for context
                context = ""
                for exchange in self.conversation_history[-3:]:  # Last 3 exchanges
                    if exchange.get("role") == "user":
                        context += f"User: {exchange['content']}\n"
                    elif exchange.get("role") == "assistant":
                        context += f"Assistant: {exchange['content']}\n"
                
                full_prompt = f"{context}User: {prompt}\nAssistant:"
            
            logger.info("🤖 Generating response...")
            
            # Check if generator is initialized
            if self.generator is None:
                raise RuntimeError("Model generator not initialized")
            
            if self.tokenizer is None:
                raise RuntimeError("Tokenizer not initialized")
            
            # Generate text
            outputs = self.generator(
                full_prompt,
                max_new_tokens=min(max_tokens, 512),  # Limit for performance
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                truncation=True,
                return_full_text=False
            )
            
            # Extract the response
            response = outputs[0]['generated_text'].strip()
            
            # Clean up the response (remove prompt echoes)
            if response.startswith("Assistant:"):
                response = response[10:].strip()
            
            # Stop at next "User:" or "Assistant:" to avoid continuation
            for stop_word in ["User:", "Assistant:", "\nUser", "\nAssistant"]:
                if stop_word in response:
                    response = response.split(stop_word)[0].strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            logger.info(f"✅ Generated {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            return "Sorry, I encountered an error generating a response."
    
    def reset_history(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_info(self):
        """Get model information"""
        return {
            "provider": "huggingface",
            "model": self.model_name,
            "device": str(self.device),
            "open_source": True,
            "offline": True,
            "cost": "Free"
        }

class LocalLLMFallback:
    """
    Local LLM with multiple fallback options
    Ensures something always works for free
    """
    
    def __init__(self):
        """Initialize with the best available model"""
        self.llm = None
        self._initialize_best_available()
    
    def _initialize_best_available(self):
        """Try different local LLM options"""
        
        # Try small efficient models first
        models_to_try = [
            "microsoft/DialoGPT-small",  # Good for conversation
            "distilgpt2",                # Smaller GPT-2
            "gpt2",                      # Original GPT-2 (always available)
        ]
        
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting to load {model_name}...")
                self.llm = HuggingFaceLLM(model_name)
                logger.info(f"✅ Successfully loaded {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {e}")
                continue
        
        if not self.llm:
            raise RuntimeError("No local LLM could be initialized")
    
    def generate(self, *args, **kwargs) -> str:
        """Generate text using the available model"""
        # Remove unsupported parameters for local models
        kwargs.pop('use_smart_prompting', None)
        
        if self.llm:
            return self.llm.generate(*args, **kwargs)
        return "No LLM available"
    
    def get_info(self):
        """Get model info"""
        if self.llm:
            return self.llm.get_info()
        return {"status": "No model loaded"}