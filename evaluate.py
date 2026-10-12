#!/usr/bin/env python3
"""Deterministic, dependency-free scoring of original responses against corrected text."""
from collections import Counter
from decimal import Decimal
from difflib import SequenceMatcher
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata

VERSION = 'content-v1'
ROOT = Path(__file__).resolve().parent
DIGITS = {'零': 0, '〇': 0, **dict(zip('一二三四五六七八九', range(1, 10)))}
DIGITS.update({'兩': 2, '两': 2, '両': 2})
SMALL = {'十': 10, '百': 100, '千': 1000}
LARGE = {'萬': 10000, '万': 10000, '億': 100000000, '亿': 100000000}
ASIAN = '零〇一二三四五六七八九兩两両十百千萬万億亿'
TOKEN = re.compile(r'\ufffd|\d{1,2}:\d{2}|(?<!\w)[+-](?:\d+(?:\.\d+)?|\.\d+)|\d+(?:\.\d+)?|\.\d+|[a-z]+(?:\x27[a-z]+)*|[^\W\d_]', re.I)
NUMBER = re.compile(r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)\Z')

def asian_number(text):
    if not any(c in SMALL or c in LARGE for c in text):
        return int(''.join(str(DIGITS.get(c, c)) for c in text))
    total = section = number = 0
    for token in re.findall(r'\d+|.', text):
        if token.isascii() and token.isdigit():
            number = int(token)
        elif token in DIGITS:
            number = DIGITS[token]
        elif token in SMALL:
            section += (number or 1) * SMALL[token]
            number = 0
        elif token in LARGE:
            total += (section + number or 1) * LARGE[token]
            section = number = 0
    return total + section + number

def normalize(text, input_name=''):
    text = html.unescape(text)
    text = re.sub(r'(?m)^\s*(?:`{3,}|~{3,}).*$', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]*>', ' ', text)
    text = re.sub(r'(?i)\[(?:\?|illegible|unreadable)\]', '\ufffd', text)
    # Line-end hyphenation is a presentation choice, not a different word.
    text = re.sub(r'([A-Za-z])-\s*\n\s*([A-Za-z])', r'\1\2', text)
    text = unicodedata.normalize('NFKC', text).casefold()
    text = text.replace('−', '-').replace('’', "'").replace('‘', "'").replace('○', '〇')
    text = re.sub(r'ます(?:〳〵|/\\)', 'ますます', text)
    text = text.replace('元年', '1年')
    def replace_asian(match):
        value = match.group()
        if not any(c in ASIAN for c in value):
            return value
        before = text[match.start()-1:match.start()]
        after = text[match.end():]
        isolated = (not before or not before.isalnum()) and (not after or not after[0].isalnum())
        numeric_context = before == '第' or bool(re.match(r'(?:以上|以下|年|月|日|人|戶|泊|巡|次|案|區|郡|陣|個|ケ|ヶ|時|分|秒|番|號|回|枚)', after))
        if isolated or numeric_context or any(c.isascii() and c.isdigit() for c in value):
            return str(asian_number(value))
        return value  # Do not turn 三笠山 or 百貨店 into numeric quantities.
    text = re.sub('[' + ASIAN + r'0-9]+', replace_asian, text)
    text = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', text)
    if input_name == 'itinerary.png':
        text = re.sub(r'(?<!\d)([0-2]?\d)[・:.](\d{2})(?!\d)', lambda m: str(int(m[1])) + ':' + m[2], text)
    tokens, numbers = [], []
    for match in TOKEN.finditer(text):
        value = match.group()
        if NUMBER.fullmatch(value):
            value = format(Decimal(value).normalize(), 'f')
            if Decimal(value) == 0:
                value = '0'
            numbers.append(value)
            tokens.append('n:' + value)
        elif re.fullmatch(r'\d{1,2}:\d{2}', value):
            numbers.append(value)
            tokens.append('n:' + value)
        else:
            tokens.append(value.replace("'", ''))
    characters = ''.join(t[2:] if t.startswith('n:') else t for t in tokens)
    return {'tokens': tokens, 'numbers': numbers, 'characters': characters}

def overlap(reference, candidate):
    expected, actual = Counter(reference), Counter(candidate)
    matched = sum((expected & actual).values())
    precision = matched / len(candidate) if candidate else (1.0 if not reference else 0.0)
    recall = matched / len(reference) if reference else 1.0
    f1 = 2 * matched / (len(reference) + len(candidate)) if reference or candidate else 1.0
    return {'precision': precision, 'recall': recall, 'f1': f1, 'matched': matched,
            'reference_count': len(reference), 'candidate_count': len(candidate),
            'missing': [{'text': k[2:] if k.startswith('n:') else k, 'count': v} for k, v in sorted((expected-actual).items())],
            'extra': [{'text': k[2:] if k.startswith('n:') else k, 'count': v} for k, v in sorted((actual-expected).items())]}

def edit_distance(left, right):
    """Exact unit-cost Levenshtein distance, using Python integers as bit vectors."""
    if len(left) > len(right):
        left, right = right, left
    if not left:
        return len(right)
    masks = {}
    for index, char in enumerate(left):
        masks[char] = masks.get(char, 0) | (1 << index)
    full = (1 << len(left)) - 1
    high = 1 << (len(left) - 1)
    positive, negative, distance = full, 0, len(left)
    for char in right:
        equal = masks.get(char, 0)
        vertical = equal | negative
        horizontal = (((equal & positive) + positive) ^ positive) | equal
        plus = negative | ~(horizontal | positive)
        minus = positive & horizontal
        distance += bool(plus & high) - bool(minus & high)
        plus = (plus << 1) | 1
        minus <<= 1
        positive = (minus | ~(vertical | plus)) & full
        negative = (plus & vertical) & full
    return distance

def score(reference, candidate, input_name=''):
    expected, actual = normalize(reference, input_name), normalize(candidate or '', input_name)
    content = overlap(expected['tokens'], actual['tokens'])
    numeric = overlap(expected['numbers'], actual['numbers'])
    distance = edit_distance(expected['characters'], actual['characters'])
    changes = []
    for tag, a, b, c, d in SequenceMatcher(None, expected['tokens'], actual['tokens'], autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        display = lambda items: [v[2:] if v.startswith('n:') else v for v in items]
        changes.append({'kind': tag, 'reference': display(expected['tokens'][a:b]),
                        'candidate': display(actual['tokens'][c:d]),
                        'before': display(expected['tokens'][max(0,a-8):a]),
                        'after': display(expected['tokens'][b:b+8])})
    return {'content': content, 'numbers': numeric,
            'character_errors': distance, 'reference_characters': len(expected['characters']),
            'cer': distance / len(expected['characters']) if expected['characters'] else float(bool(actual['characters'])),
            'normalized_reference': expected['characters'], 'normalized_candidate': actual['characters'],
            'changes': changes}

def evaluate_runs(runs):
    references = {}
    for run in runs:
        for task in run['tasks']:
            name = task['input']
            if name not in references:
                path = ROOT / 'corrected' / (Path(name).stem + '.md')
                text = path.read_text()
                if not text.strip():
                    raise ValueError('Empty ground truth: ' + str(path))
                references[name] = {'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest(),
                                    'path': str(path.relative_to(ROOT))}
            reference = references[name]
            task['evaluation'] = score(reference['text'], task['output'], name)
            task['evaluation']['reference_sha256'] = reference['sha256']
            task['evaluation']['candidate_sha256'] = hashlib.sha256((task['output'] or '').encode()).hexdigest()
            task['evaluation']['no_response'] = not bool(task['output'])
        scores = [t['evaluation'] for t in run['tasks']]
        run['evaluation'] = {'macro_content_f1': sum(s['content']['f1'] for s in scores)/len(scores),
                             'macro_numeric_f1': sum(s['numbers']['f1'] for s in scores)/len(scores),
                             'macro_cer': sum(s['cer'] for s in scores)/len(scores), 'tasks': len(scores)}
    return {'version': VERSION, 'references': references,
            'method': 'Exact multiset token F1: Latin words, individual CJK characters, atomic numbers. Macro means weight each input equally; missing responses score zero. Character error rate is an ordered diagnostic, not part of ranking.'}

if __name__ == '__main__':
    import importlib.util
    spec = importlib.util.spec_from_file_location('dashboard', ROOT / 'results/build-index.py')
    dashboard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dashboard)
    data = dashboard.collect()
    if 'evaluation' not in data:
        data['evaluation'] = evaluate_runs(data['runs'])
    report = ROOT / 'results/evaluation.json'
    report.write_text(json.dumps({k:v for k,v in data.items() if k!='images'}, ensure_ascii=False, indent=2) + '\n')
    for run in sorted(data['runs'], key=lambda r: r['evaluation']['macro_content_f1'], reverse=True):
        print(f'{run["name"]:28} content={run["evaluation"]["macro_content_f1"]:7.2%} numbers={run["evaluation"]["macro_numeric_f1"]:7.2%}')
