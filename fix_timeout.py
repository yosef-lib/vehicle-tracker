
import re
with open('bot/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('async with httpx.AsyncClient() as client:', 'async with httpx.AsyncClient(timeout=120.0) as client:')

with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.write(code)

