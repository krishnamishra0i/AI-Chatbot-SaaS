#!/usr/bin/env python
"""
Quick test of improved RAG vs LLM system
"""
import sys
sys.path.append('.')

async def quick_test():
    from backend.utils.enhanced_chat_system import enhanced_chat_system

    print('Testing improved system...')

    # Test simple greeting
    print('\n1. Testing "Hii":')
    retriever = enhanced_chat_system.rag_retriever
    results = retriever.retrieve_context('Hii')
    print(f'RAG results: {len(results)}')
    if results:
        print(f'Top confidence: {results[0].confidence:.2f}')

    chunks = []
    async for chunk in enhanced_chat_system.generate_response_stream('Hii'):
        chunks.append(chunk)
    response = "".join(chunks).strip()
    print(f'Response: {response}')

    # Test LMS question
    print('\n2. Testing "what is lms":')
    results = retriever.retrieve_context('what is lms')
    print(f'RAG results: {len(results)}')
    if results:
        print(f'Top confidence: {results[0].confidence:.2f}')

    chunks = []
    async for chunk in enhanced_chat_system.generate_response_stream('what is lms'):
        chunks.append(chunk)
    response = "".join(chunks).strip()
    print(f'Response: {response}')

if __name__ == "__main__":
    import asyncio
    asyncio.run(quick_test())