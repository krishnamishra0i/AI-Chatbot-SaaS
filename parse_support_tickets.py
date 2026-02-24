#!/usr/bin/env python3
"""
Parse support tickets data and convert to JSON
"""
import json
import re

def parse_support_tickets(text):
    """
    Parse the tab-separated support tickets data
    """
    lines = text.strip().split('\n')
    documents = []
    current_subject = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Check if line contains tabs
        parts = line.split('\t')
        num_parts = len(parts)

        if num_parts >= 3:
            # Question | Answer | Subject
            question = parts[0].strip()
            answer = parts[1].strip()
            subject = parts[2].strip()
            if question and answer:
                documents.append({
                    'id': f'support_{len(documents) + 1}',
                    'question': question,
                    'answer': answer,
                    'category': subject if subject else current_subject,
                    'tags': ['support', 'ticket']
                })
            if subject:
                current_subject = subject
        elif num_parts == 2:
            # Question | Answer
            question = parts[0].strip()
            answer = parts[1].strip()
            if question and answer:
                documents.append({
                    'id': f'support_{len(documents) + 1}',
                    'question': question,
                    'answer': answer,
                    'category': current_subject,
                    'tags': ['support', 'ticket']
                })
        elif num_parts == 1:
            # Subject/Category
            subject = parts[0].strip()
            if subject and subject not in ['Questions', 'Answers']:
                current_subject = subject

        i += 1

    return documents

def main():
    # Read the support tickets data from file
    with open('support_tickets_raw.txt', 'r', encoding='utf-8') as f:
        support_data = f.read()

    documents = parse_support_tickets(support_data)

    # Save to JSON
    with open('data/support_tickets.json', 'w', encoding='utf-8') as f:
        json.dump({"documents": documents}, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted {len(documents)} support tickets to JSON")

if __name__ == "__main__":
    main()