import requests
import sys

try:
    r = requests.post('http://localhost:8000/api/chat/stream', json={'message':'Tell me a short joke','use_knowledge_base': False}, stream=True, timeout=20)
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('content-type'))
    for i, line in enumerate(r.iter_lines()):
        if line:
            try:
                s = line.decode('utf-8')
            except Exception:
                s = str(line)
            print(f'LINE {i}:', s)
        if i >= 10:
            break
except Exception as e:
    print('Error:', e)
    sys.exit(1)
