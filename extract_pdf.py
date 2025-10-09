import sys
from PyPDF2 import PdfReader

path = 'Synopsis_IV[1] (1).pdf'
try:
    reader = PdfReader(path)
    print(f'PAGES={len(reader.pages)}')
    for i, page in enumerate(reader.pages):
        print(f"\n--- PAGE {i+1} START ---")
        text = page.extract_text() or ''
        text = '\n'.join(line.strip() for line in text.splitlines())
        print(text[:2000])
        if len(text) > 2000:
            print('\n[...truncated...]')
        print(f"--- PAGE {i+1} END ---\n")
except Exception as e:
    print('ERROR', e)
