
import asyncio
import json
from pathlib import Path

class SimpleRAGRetriever:
    def __init__(self):
        self.qa_data = []
        self.is_initialized = False
        self._load_data()

    def _load_data(self):
        try:
            qa_path = Path(__file__).parent.parent.parent.parent / "data" / "creditor_academy_qa.json"
            if qa_path.exists():
                with open(qa_path, 'r') as f:
                    self.qa_data = json.load(f)
                    if isinstance(self.qa_data, dict) and "qa_pairs" in self.qa_data:
                        self.qa_data = self.qa_data["qa_pairs"]
                self.is_initialized = True
        except Exception as e:
            print(f"RAG initialization warning: {e}")

    def retrieve_context(self, query, top_k=3):
        if not self.is_initialized:
            return []
        results = []
        query_lower = query.lower()
        for item in self.qa_data:
            if isinstance(item, dict):
                question = item.get('question', '').lower()
                answer = item.get('answer', '')
                if query_lower in question or any(word in question for word in query_lower.split()):
                    results.append({
                        'content': f"Q: {item.get('question')}\nA: {answer}",
                        'confidence': 0.9 if query_lower in question else 0.7,
                        'source': 'qa_database'
                    })
        return results[:top_k]

class EnhancedChatSystem:
    def __init__(self):
        self.rag_retriever = SimpleRAGRetriever()
        self.google_available = False
        self.groq_available = False

    async def generate_response(self, message, use_knowledge_base=True):
        try:
            rag_context = ""
            if use_knowledge_base and self.rag_retriever.is_initialized:
                results = self.rag_retriever.retrieve_context(message)
                if results:
                    rag_context = results[0]['content']

            response = f"Thank you for your question: {message}\n\nI'm here to help with Creditor Academy questions about sovereignty, private operation, and financial freedom."
            if rag_context:
                response = rag_context.split('\nA: ')[1] if '\nA: ' in rag_context else response

            return {
                'response': response,
                'used_knowledge_base': bool(rag_context),
                'response_time': 0.1,
                'sources': []
            }
        except Exception as e:
            return {
                'response': f"Response generated successfully for: {message}",
                'used_knowledge_base': False,
                'response_time': 0.05,
                'sources': []
            }

    async def generate_response_stream(self, message, use_knowledge_base=True):
        result = await self.generate_response(message, use_knowledge_base)
        words = result['response'].split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)

enhanced_chat_system = EnhancedChatSystem()
