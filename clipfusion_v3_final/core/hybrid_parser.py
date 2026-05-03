import json
import re

def parse_ai_response(response_text: str):
    clean = re.sub(r'```json\s*|\s*```', '', response_text.strip())

    # tenta extrair array JSON com brackets balanceados
    def extract_balanced(text, open_char, close_char):
        start = text.find(open_char)
        if start == -1:
            return None
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
        return None

    # tenta array primeiro, depois objeto
    for open_c, close_c in [('[', ']'), ('{', '}')]:
        chunk = extract_balanced(clean, open_c, close_c)
        if chunk:
            try:
                data = json.loads(chunk)
                if isinstance(data, list):
                    return data
                else:
                    return [data]
            except:
                continue

    return None

def validate_ai_cut(cut):
    required = ['start', 'end', 'title', 'hook', 'score']
    for field in required:
        if field not in cut:
            return False
    return True
