#!/usr/bin/env python3
"""
CHROMADB CLOUD INTEGRATION SYSTEM
Stores all 200+ answers in ChromaDB Cloud for semantic search and improved accuracy
"""

import chromadb
import json
from comprehensive_answer_system import ComprehensiveAnswerSystem

class ChromaDBIntegration:
    """Integration with ChromaDB Cloud for answer storage and retrieval"""
    
    def __init__(self, api_key, tenant_id, database_name):
        """Initialize ChromaDB Cloud client"""
        try:
            self.client = chromadb.CloudClient(
                api_key=api_key,
                tenant=tenant_id,
                database=database_name
            )
            print("✅ Connected to ChromaDB Cloud successfully!")
            self.connected = True
        except Exception as e:
            print(f"❌ Failed to connect to ChromaDB Cloud: {e}")
            self.connected = False
            self.client = None
    
    def upload_answers(self, comprehensive_system):
        """Upload all answers from comprehensive system to ChromaDB"""
        if not self.connected:
            print("❌ Cannot upload - not connected to ChromaDB")
            return False
        
        try:
            # Get all answers from comprehensive system
            answers_db = comprehensive_system.answers
            question_list = []
            answer_list = []
            metadata_list = []
            id_list = []
            
            print(f"\n📤 Uploading {len(answers_db)} answers to ChromaDB Cloud...")
            
            for idx, (question, answer) in enumerate(answers_db.items()):
                if question == 'default':
                    continue
                
                question_list.append(question)
                answer_list.append(answer)
                
                # Categorize questions
                if 'creditor academy' in question.lower() or 'freedom formula' in question.lower() or 'sovereignty' in question.lower():
                    category = 'creditor_academy'
                elif any(tech in question.lower() for tech in ['ai', 'python', 'cloud', 'aws', 'database', 'programming']):
                    category = 'technology'
                elif any(biz in question.lower() for biz in ['business', 'marketing', 'finance', 'investment', 'entrepreneurship']):
                    category = 'business'
                else:
                    category = 'general'
                
                metadata_list.append({
                    'category': category,
                    'answer_length': len(answer.split()),
                    'question_length': len(question.split())
                })
                
                id_list.append(f"answer_{idx}")
            
            # Create or get collection
            collection = self.client.get_or_create_collection(
                name="creditor_academy_answers",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Add all answers to collection
            collection.add(
                ids=id_list,
                documents=question_list,
                metadatas=metadata_list,
                embeddings=None  # Let ChromaDB generate embeddings
            )
            
            print(f"✅ Successfully uploaded {len(question_list)} answers to ChromaDB!")
            print(f"   Collection: creditor_academy_answers")
            print(f"   Categories: Creditor Academy, Technology, Business, General")
            
            return True
            
        except Exception as e:
            print(f"❌ Error uploading answers: {e}")
            return False
    
    def search_answers(self, query, num_results=3):
        """Search ChromaDB for similar answers"""
        if not self.connected:
            return []
        
        try:
            collection = self.client.get_collection(name="creditor_academy_answers")
            results = collection.query(
                query_texts=[query],
                n_results=num_results
            )
            return results
        except Exception as e:
            print(f"❌ Error searching ChromaDB: {e}")
            return []
    
    def get_answer_with_context(self, query):
        """Get answer using ChromaDB semantic search + local system"""
        # First try ChromaDB semantic search
        if self.connected:
            results = self.search_answers(query, num_results=1)
            if results and results['documents'] and len(results['documents']) > 0:
                matched_question = results['documents'][0][0] if results['documents'][0] else None
                
                if matched_question:
                    comprehensive = ComprehensiveAnswerSystem()
                    answer = comprehensive.answers.get(matched_question, None)
                    
                    if answer:
                        return {
                            'answer': answer,
                            'confidence': 0.95,
                            'method': 'chromadb_semantic_search',
                            'matched_question': matched_question,
                            'source': 'chromadb_cloud'
                        }
        
        # Fallback to local comprehensive system
        comprehensive = ComprehensiveAnswerSystem()
        return comprehensive.get_answer(query)


def test_chromadb_integration():
    """Test ChromaDB Cloud integration"""
    
    print("\n" + "="*100)
    print("🧪 TESTING CHROMADB CLOUD INTEGRATION")
    print("="*100)
    
    # Your ChromaDB Cloud credentials
    api_key = 'ck-BMAgXpD2WFAgi82jm7AkLyVk1kN7qrkk2sndKqAVMFXR'
    tenant_id = '8e799f6a-8e13-491e-8daa-ea89d5f2bf89'
    database_name = 'lms-chatbot'
    
    # Initialize ChromaDB integration
    print("\n🔗 Connecting to ChromaDB Cloud...")
    chroma_system = ChromaDBIntegration(api_key, tenant_id, database_name)
    
    if chroma_system.connected:
        print("✅ ChromaDB Cloud connection successful!")
        
        # Load comprehensive answer system
        print("\n📚 Loading comprehensive answer system...")
        comprehensive = ComprehensiveAnswerSystem()
        print(f"✅ Loaded {len(comprehensive.answers)} answers")
        
        # Upload answers to ChromaDB
        print("\n📤 Uploading answers to ChromaDB Cloud...")
        success = chroma_system.upload_answers(comprehensive)
        
        if success:
            print("\n✅ All answers uploaded successfully!")
            
            # Test semantic search
            print("\n🔍 Testing semantic search with ChromaDB...")
            test_queries = [
                "what is creditor academy",
                "how does machine learning work",
                "explain business and marketing"
            ]
            
            for query in test_queries:
                print(f"\n  Query: {query}")
                result = chroma_system.get_answer_with_context(query)
                print(f"  Answer: {result['answer'][:100]}...")
                print(f"  Confidence: {result['confidence']}")
                print(f"  Method: {result['method']}")
        else:
            print("❌ Failed to upload answers")
    else:
        print("❌ Could not connect to ChromaDB Cloud")
        print("   Check your API key, tenant ID, and database name")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    test_chromadb_integration()
