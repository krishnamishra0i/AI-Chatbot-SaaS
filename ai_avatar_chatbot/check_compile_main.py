import traceback, sys
try:
    s = open('backend/main.py','r', encoding='utf-8').read()
    compile(s, 'backend/main.py', 'exec')
    print('OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
