#!/usr/bin/env python3
"""
Enhanced Integrated Answer System - With Clear API Logging
Shows when and why LLM/APIs are used
"""

import os
import json
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClearAPIAnswerSystem:
    """Answer system with clear visibility into when APIs are used"""
    
    def __init__(self):
        """Initialize with comprehensive system and API clients"""
        print("[INIT] Loading answer systems...")
        
        # Layer 1: Comprehensive
        try:
            from comprehensive_answer_system import ComprehensiveAnswerSystem
            self.comprehensive = ComprehensiveAnswerSystem()
            print(f"[OK] Comprehensive System: {len(self.comprehensive.answers)} answers loaded")
        except Exception as e:
            print(f"[ERROR] Comprehensive: {e}")
            self.comprehensive = None
        
        # Layer 2: ChromaDB
        try:
            if Path('chromadb_answers_backup.json').exists():
                with open('chromadb_answers_backup.json') as f:
                    self.chromadb_data = json.load(f)
                print(f"[OK] ChromaDB Backup: {len(self.chromadb_data)} answers")
            else:
                self.chromadb_data = None
        except:
            self.chromadb_data = None
        
        # Layer 3&4: APIs
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
        if self.google_key:
            print(f"[OK] Google API: Configured")
        else:
            print(f"[WARNING] Google API: Not configured")
            
        if self.groq_key:
            print(f"[OK] Groq API: Configured")
        else:
            print(f"[WARNING] Groq API: Not configured")
    
    def get_answer_with_details(self, question: str) -> Dict:
        """Get answer and show exactly which layer was used"""
        
        print(f"\n{'='*80}")
        print(f"PROCESSING: {question}")
        print(f"{'='*80}")
        
        # Layer 1: Comprehensive
        if self.comprehensive:
            result = self.comprehensive.get_answer(question)
            confidence = result.get('confidence', 0)
            
            print(f"\n[LAYER 1] Comprehensive System")
            print(f"  Confidence: {confidence}")
            print(f"  Answer: {result['answer'][:100]}...")
            
            if confidence >= 0.7:
                print(f"  STATUS: [ACCEPTED] - High confidence answer")
                return {
                    'answer': result['answer'],
                    'source': 'Comprehensive System',
                    'layer': 1,
                    'confidence': confidence,
                    'api_used': False
                }
            else:
                print(f"  STATUS: [REJECTED] - Confidence too low, trying fallback...")
        
        # Layer 2: ChromaDB
        if self.chromadb_data:
            print(f"\n[LAYER 2] ChromaDB Cloud")
            # Simple keyword matching - STRICT threshold
            best_match = None
            best_score = 0
            for item in self.chromadb_data:
                q = item.get('question', '').lower()
                score = sum(1 for word in q.split() if word in question.lower())
                if score > best_score:
                    best_score = score
                    best_match = item
            
            # STRICT: Need at least 3 keyword matches AND exact phrase match
            has_exact_match = any(q in question.lower() for q in [item.get('question', '').lower() for item in self.chromadb_data if item])
            
            if best_match and best_score >= 4 and has_exact_match:
                print(f"  Keyword Match Score: {best_score} (STRICT)")
                print(f"  Answer: {best_match['answer'][:100]}...")
                print(f"  STATUS: [ACCEPTED] - Strong semantic match found")
                return {
                    'answer': best_match['answer'],
                    'source': 'ChromaDB Cloud',
                    'layer': 2,
                    'confidence': 0.85,
                    'api_used': False
                }
            else:
                print(f"  Match Score: {best_score} (below strict threshold)")
                print(f"  STATUS: [REJECTED] - Weak match, using LLM/API for better answer...")
        
        # Layer 3: Groq API
        if self.groq_key:
            print(f"\n[LAYER 3] Groq Mixtral API")
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_key)
                
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {"role": "user", "content": question}
                    ],
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content
                print(f"  API Response: {answer[:100]}...")
                print(f"  STATUS: [ACCEPTED] - Generated by Groq API")
                return {
                    'answer': answer,
                    'source': 'Groq Mixtral API',
                    'layer': 3,
                    'confidence': 0.85,
                    'api_used': True
                }
            except Exception as e:
                print(f"  ERROR: {str(e)[:100]}")
                print(f"  Trying Google API...")
        
        # Layer 4: Google API
        if self.google_key:
            print(f"\n[LAYER 4] Google Gemini API")
            try:
                import google.genai as genai
                client = genai.Client(api_key=self.google_key)
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=question
                )
                
                answer = response.text
                print(f"  API Response: {answer[:100]}...")
                print(f"  STATUS: [ACCEPTED] - Generated by Google API")
                return {
                    'answer': answer,
                    'source': 'Google Gemini API',
                    'layer': 4,
                    'confidence': 0.85,
                    'api_used': True
                }
            except Exception as e:
                if "quota" in str(e).lower() or "429" in str(e):
                    print(f"  NOTE: Google quota exceeded (expected with free tier)")
                else:
                    print(f"  ERROR: {str(e)[:100]}")
        
        # Default fallback
        print(f"\n[FALLBACK] Default Response")
        return {
            'answer': "I don't have a good answer for that. Please try asking about Creditor Academy, technology, business, or other topics I'm trained on.",
            'source': 'Default Fallback',
            'layer': 5,
            'confidence': 0.3,
            'api_used': False
        }


def main():
    """Test the system with various questions"""
    
    print("\n" + "█"*80)
    print("█" + " "*20 + "TESTING ANSWER GENERATION SYSTEM WITH APIs" + " "*18 + "█")
    print("█"*80)
    
    system = ClearAPIAnswerSystem()
    
    # Test questions - mix of known and unknown
    test_questions = [
        "What is Creditor Academy?",  # Should use Comprehensive (0.99)
        "Tell me about artificial intelligence",  # Mixed confidence
        "What is your favorite pizza?",  # Unknown - should use API
        "How do I become financially free?",  # Business question
        "Write me a poem about Python",  # Creative - should use API
    ]
    
    for question in test_questions:
        result = system.get_answer_with_details(question)
        print(f"\n[RESULT] Used Layer {result['layer']}: {result['source']}")
        print(f"[API USED]: {result['api_used']}")
        print(f"[CONFIDENCE]: {result['confidence']}")
    
    print("\n" + "█"*80)
    print("█" + " "*25 + "TEST COMPLETE" + " "*44 + "█")
    print("█"*80 + "\n")


if __name__ == "__main__":
    main()
