"""
LLM (Large Language Model) interface
"""
from typing import Optional, List, Tuple
from backend.utils.logger import setup_logger
from backend.llm.prompt import SYSTEM_PROMPT, RAG_PROMPT, BASIC_QA_PROMPT, CONFIDENCE_SCORING_PROMPT

logger = setup_logger(__name__)

class LLMInterface:
    """Interface for LLM providers"""

    def __init__(self, provider="groq", model="gemma-7b-it", base_url="http://localhost:11434"):
        """
        Initialize LLM

        Args:
            provider: LLM provider (groq, ollama, openai)
            model: Model name
            base_url: Base URL for local LLM services
        """
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.conversation_history = []

        # Initialize offline chatbot for fallback
        try:
            import sys
            import os
            # Add project root to path for offline chatbot import
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            sys.path.insert(0, project_root)
            from offline_chatbot import OfflineChatbot
            self.offline_chatbot = OfflineChatbot()
            logger.info("✅ Offline chatbot initialized for API fallback")
        except Exception as e:
            logger.warning(f"Offline chatbot initialization failed: {e}")
            self.offline_chatbot = None

        try:
            if provider == "groq":
                self._init_groq()
            elif provider == "ollama":
                self._init_ollama()
            elif provider == "openai":
                self._init_openai()
            else:
                logger.warning(f"Provider {provider} not fully configured")
        except Exception as e:
            logger.warning(f"LLM init failed ({provider}): {e}. Falling back to DummyLLM for dev.")
            # Simple local fallback for development when external LLMs are unavailable
            self.provider = "dummy"
            class DummyLLM:
                def __init__(self):
                    self.name = "DummyLLM"
                def generate(self, prompt, *args, **kwargs):
                    return "(dev) Model not available; this is a placeholder response."
                async def generate_async(self, prompt, *args, **kwargs):
                    yield "(dev) Model not available; this is a placeholder response."
                def get_models(self):
                    return ["dummy-model"]
                def chat(self, message, context=None):
                    return "(dev) Model not available; this is a placeholder response."
            self.dummy_client = DummyLLM()
    
    def _init_groq(self):
        """Initialize Groq client (Real-time, fastest LLM)"""
        try:
            from backend.llm.groq_llm import GroqLLM
            self.groq_client = GroqLLM(model=self.model)
            logger.info(f"✅ Using Groq (Real-time LLM) with model: {self.model}")
        except ImportError as e:
            logger.error(f"Groq initialization failed: {e}")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            import requests
            self.requests = requests
            logger.info(f"Using Ollama with model: {self.model}")
        except ImportError:
            logger.error("requests library not installed")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI()
            logger.info(f"Using OpenAI with model: {self.model}")
        except ImportError:
            logger.error("openai library not installed")
            raise
    
    def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, system_prompt: Optional[str] = None, use_smart_prompting: bool = False) -> str:
        """
        Generate response from LLM with enhanced error handling
        
        Args:
            prompt: User prompt
            context: Optional context from RAG
            max_tokens: Maximum tokens in response
            temperature: Temperature for creativity control
            system_prompt: Custom system prompt
            use_smart_prompting: Enable intelligent prompt selection
            
        Returns:
            Generated response
        """
        try:
            if self.provider == "groq":
                return self._generate_groq(prompt, context, max_tokens, temperature, system_prompt, use_smart_prompting)
            elif self.provider == "ollama":
                return self._generate_ollama(prompt, context)
            elif self.provider == "openai":
                return self._generate_openai(prompt, context)
            elif self.provider == "dummy":
                return self.dummy_client.generate(prompt)
            else:
                return "Provider not supported"
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            error_message = str(e).lower()

            # Enhanced fallback system for API errors
            if any(keyword in error_message for keyword in ["429", "rate limit", "too many requests", "api error", "groq api error"]):
                logger.warning("API rate limit detected, trying enhanced offline fallback")

                # Try offline chatbot first for comprehensive answers
                if self.offline_chatbot:
                    try:
                        offline_result = self.offline_chatbot.chat(prompt)
                        if offline_result and offline_result.get("confidence", 0) > 0.7:
                            logger.info("✅ Used enhanced offline chatbot due to API rate limit")
                            return offline_result["response"]
                    except Exception as offline_error:
                        logger.error(f"Offline chatbot fallback failed: {offline_error}")

                # Fallback to basic knowledge base
                if self._is_basic_question(prompt):
                    kb_answer = self._get_basic_knowledge_answer(prompt)
                    if kb_answer:
                        logger.info("✅ Used knowledge base fallback due to API rate limit")
                        return kb_answer

                # Final fallback with helpful guidance
                return """I'm currently experiencing high API demand, but I can still help with comprehensive AI answers!

🔹 **What is AI?** - Computer systems performing human-like tasks through learning and reasoning
🔹 **Machine Learning** - Algorithms that improve performance through data exposure
🔹 **Neural Networks** - Brain-inspired computing systems with interconnected nodes
🔹 **Deep Learning** - Multi-layered neural networks for complex problem solving
🔹 **Computer Vision** - AI systems that understand and interpret visual information

Try asking about any of these topics for detailed explanations!"""

            # Try knowledge base fallback for basic questions on other errors
            if self._is_basic_question(prompt):
                kb_answer = self._get_basic_knowledge_answer(prompt)
                if kb_answer:
                    logger.info("✅ Used knowledge base fallback due to LLM error")
                    return kb_answer

            # Try offline chatbot for other errors
            if self.offline_chatbot:
                try:
                    offline_result = self.offline_chatbot.chat(prompt)
                    if offline_result and offline_result.get("confidence", 0) > 0.5:
                        logger.info("✅ Used offline chatbot fallback")
                        return offline_result["response"]
                except Exception as offline_error:
                    logger.error(f"Offline chatbot fallback failed: {offline_error}")

            return "I'm experiencing technical difficulties. For comprehensive AI answers, try asking about artificial intelligence, machine learning, or neural networks."
    
    def generate_with_confidence(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, system_prompt: Optional[str] = None, kb_confidence: float = 0.0) -> Tuple[str, float]:
        """
        Generate response with confidence score
        
        Returns:
            Tuple of (response, confidence_score)
        """
        response = self.generate(prompt, context, max_tokens, temperature, system_prompt)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(response, prompt, context, kb_confidence)
        
        return response, confidence
    
    def _calculate_confidence(self, answer: str, question: str, context: Optional[str] = None, kb_confidence: float = 0.0) -> float:
        """Calculate confidence score for the answer"""
        try:
            # Base confidence from answer quality
            confidence_score = 0.5
            
            # Increase confidence if answer is detailed
            if len(answer) > 50:
                confidence_score += 0.2
            
            # Increase if context was provided and used
            if context and len(context) > 10:
                confidence_score += 0.2
            
            # Factor in knowledge base confidence
            confidence_score = (confidence_score + kb_confidence) / 2.0
            
            # Decrease if answer contains uncertainty words
            uncertainty_words = ["i'm not sure", "uncertain", "maybe", "perhaps", "could be"]
            if any(word in answer.lower() for word in uncertainty_words):
                confidence_score -= 0.3
            
            # Cap between 0 and 1
            confidence_score = max(0.0, min(1.0, confidence_score))
            
            return confidence_score
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5  # Default medium confidence
    
    async def generate_async(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7, system_prompt: Optional[str] = None):
        """
        Generate response asynchronously with streaming support
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for creativity control
            system_prompt: Custom system prompt
            
        Yields:
            Text chunks for streaming
        """
        try:
            if self.provider == "groq" and hasattr(self, 'groq_client'):
                async for chunk in self.groq_client.generate_async(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt
                ):
                    yield chunk
            else:
                # Fallback for non-streaming providers
                result = self.generate(prompt, max_tokens=max_tokens, temperature=temperature, system_prompt=system_prompt)
                yield result
        except Exception as e:
            logger.error(f"Async generation error: {e}")
            yield "Sorry, I encountered an error processing your request."
    
    def _generate_groq(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, system_prompt: Optional[str] = None, use_smart_prompting: bool = False) -> str:
        """Generate using Groq (Real-time inference)"""
        # Check knowledge base first for basic questions
        if self._is_basic_question(prompt):
            knowledge_answer = self._get_basic_knowledge_answer(prompt)
            if knowledge_answer:
                return knowledge_answer

        # Select appropriate prompt based on question type
        if self._is_basic_question(prompt):
            if context:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt) + f"\n\nContext: {context}"
            else:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt)
        else:
            if context:
                full_prompt = RAG_PROMPT.format(context=context, question=prompt)
            else:
                full_prompt = prompt
        
        try:
            if use_smart_prompting:
                # Use smart prompt selection
                smart_system_prompt = self.groq_client.get_smart_system_prompt(prompt)
                response = self.groq_client.generate(
                    prompt=full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=smart_system_prompt
                )
            else:
                # Use provided system prompt or default
                response = self.groq_client.generate(
                    prompt=full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt or SYSTEM_PROMPT
                )
            return response
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return "Error generating response from Groq API"
    
    def _is_basic_question(self, question: str) -> bool:
        """Determine if a question is basic (simple factual or how-to)"""
        question_lower = question.lower().strip()

        # Basic question indicators - more precise detection
        basic_patterns = [
            "what is", "what are", "what does", "what do",
            "how do", "how to", "how does", "how can",
            "where is", "where can", "where do",
            "when is", "when do", "when does",
            "why is", "why do", "why does",
            "who is", "who are", "who does",
            "which is", "which are",
            "is it", "are there", "does it", "do you",
            "can you", "will you", "should i",
            "tell me", "explain", "define", "meaning"
        ]

        # Complex question indicators - if these are present, it's not basic
        complex_indicators = [
            "compare", "difference", "versus", "vs", "versus",
            "analyze", "evaluate", "complex", "advanced",
            "integrate", "implement", "develop", "create",
            "optimize", "troubleshoot", "debug", "fix",
            "architecture", "design", "strategy", "plan"
        ]

        # Check for complex indicators first
        for indicator in complex_indicators:
            if indicator in question_lower:
                return False

        # Check if question starts with basic patterns
        for pattern in basic_patterns:
            if question_lower.startswith(pattern):
                # Additional check: if it's a very long basic question, it might be complex
                word_count = len(question.split())
                if word_count > 20:
                    return False
                return True

        # Check question length (basic questions are usually shorter)
        word_count = len(question.split())
        if word_count <= 12 and question.count("?") <= 2:
            return True

        return False

    def _get_basic_knowledge_answer(self, question: str) -> Optional[str]:
        """Get pre-verified answers for common basic questions"""
        question_lower = question.lower().strip()

        # Knowledge base for maximum accuracy
        knowledge_base = {
            "what is ai": "AI, or Artificial Intelligence, is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, problem-solving, perception, and language understanding. AI systems are designed to perform tasks that typically require human intelligence.",

            "what is machine learning": "Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to analyze data, identify patterns, and make predictions or decisions.",

            "how does machine learning work": "Machine Learning works through these key steps: 1) Data Collection - gathering relevant data, 2) Data Preparation - cleaning and organizing data, 3) Model Training - using algorithms to learn patterns, 4) Model Evaluation - testing accuracy, 5) Deployment - using the model for predictions. The model improves over time as it processes more data.",

            "what is deep learning": "Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers to model complex patterns in data. It's particularly effective for tasks like image recognition, natural language processing, and speech recognition.",

            "what is natural language processing": "Natural Language Processing (NLP) is a field of AI that focuses on enabling computers to understand, interpret, and generate human language. It combines computational linguistics with statistical and machine learning models.",

            "what is computer vision": "Computer Vision is a field of AI that trains computers to interpret and understand visual information from the world. It enables machines to identify objects, people, text, and scenes in images and videos.",

            "how do neural networks work": "Neural networks work by mimicking the human brain's structure. They consist of interconnected nodes (neurons) organized in layers. Each connection has a weight that adjusts during training. Data flows through the network, and the system learns by adjusting these weights to minimize errors in predictions.",

            "what is supervised learning": "Supervised Learning is a type of machine learning where the algorithm learns from labeled training data. The model is trained on input-output pairs and learns to predict outputs for new, unseen inputs. Examples include classification and regression tasks.",

            "what is unsupervised learning": "Unsupervised Learning is a type of machine learning where the algorithm learns patterns from unlabeled data. It discovers hidden structures or groupings in data without explicit guidance. Examples include clustering and dimensionality reduction.",

            "what is reinforcement learning": "Reinforcement Learning is a type of machine learning where an agent learns by interacting with an environment. It receives rewards or penalties for actions and learns to maximize cumulative rewards over time. It's commonly used in game playing and robotics."
        }

        # Check for exact matches first
        for key, answer in knowledge_base.items():
            if key in question_lower or question_lower in key:
                return answer

        return None
    
    def is_greeting(self, message: str) -> bool:
        """Check if the message is a simple greeting."""
        greetings = [
            "hello", "hi", "hii", "hey", "heyy", "good morning", 
            "good afternoon", "good evening", "greetings", "howdy"
        ]
        # Normalize message
        message_lower = message.lower().strip("!?. ")
        
        # Check if it's a simple greeting (1-2 words)
        if message_lower in greetings and len(message_lower.split()) <= 2:
            return True
        return False
    
    def _generate_ollama(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate using Ollama"""
        # Check knowledge base first for basic questions
        if self._is_basic_question(prompt):
            knowledge_answer = self._get_basic_knowledge_answer(prompt)
            if knowledge_answer:
                return knowledge_answer

        # Select appropriate prompt based on question type
        if self._is_basic_question(prompt):
            if context:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt) + f"\n\nContext: {context}"
            else:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt)
        else:
            if context:
                full_prompt = RAG_PROMPT.format(context=context, question=prompt)
            else:
                full_prompt = prompt
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False}
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "Error generating response"
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return "Unable to connect to LLM service"
    
    def _generate_openai(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate using OpenAI"""
        # Check knowledge base first for basic questions
        if self._is_basic_question(prompt):
            knowledge_answer = self._get_basic_knowledge_answer(prompt)
            if knowledge_answer:
                return knowledge_answer

        # Select appropriate prompt based on question type
        if self._is_basic_question(prompt):
            if context:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt) + f"\n\nContext: {context}"
            else:
                full_prompt = BASIC_QA_PROMPT.format(question=prompt)
        else:
            if context:
                full_prompt = RAG_PROMPT.format(context=context, question=prompt)
            else:
                full_prompt = prompt
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return content if content else "Error: No response generated"
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "Error generating response"
    
    def chat(self, message: str, context: Optional[str] = None) -> str:
        """
        Chat with history
        
        Args:
            message: User message
            context: Optional RAG context
            
        Returns:
            Assistant response
        """
        self.conversation_history.append({"role": "user", "content": message})
        
        response = self.generate(message, context)
        
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
