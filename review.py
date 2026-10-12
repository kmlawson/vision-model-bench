"""Presentation-only source highlights; scoring remains in evaluate.py."""
from collections import Counter
from difflib import SequenceMatcher
import re
from evaluate import ASIAN, normalize

VISIBLE = re.compile(r'\[(?:\?|illegible|unreadable)\]|[+−-]?\d+(?:,\d{3})*(?:\.\d+)?|[A-Za-z]+(?:[’\x27][A-Za-z]+)*|[' + ASIAN + r']+|[^\W\d_]', re.I)


def annotate(reference, candidate, input_name=''):
    if not candidate:
        return []
    expected = normalize(reference, input_name)['tokens']
    actual = normalize(candidate, input_name)['tokens']
    rough, origins = [], []
    for match in VISIBLE.finditer(candidate):
        for token in normalize(match.group(), input_name)['tokens']:
            rough.append(token)
            origins.append((match.start(), match.end()))
    mapped = [None] * len(actual)
    for tag, a, b, c, d in SequenceMatcher(None, rough, actual, autojunk=False).get_opcodes():
        if tag == 'equal' or (tag == 'replace' and b-a == d-c):
            mapped[c:d] = origins[a:b]
        elif tag == 'replace' and b > a:
            mapped[c:d] = [(origins[a][0], origins[b-1][1])] * (d-c)
    matched = [False] * len(actual)
    hints = ['Extra content; no corresponding ground-truth text.'] * len(actual)
    remaining = Counter(expected)
    opcodes = SequenceMatcher(None, expected, actual, autojunk=False).get_opcodes()
    # Assign exact contextual matches first, then formatting-tolerant reordered matches.
    for tag, a, b, c, d in opcodes:
        if tag == 'equal':
            for i in range(c,d):
                matched[i] = True
                remaining[actual[i]] -= 1
        elif tag == 'replace':
            display = lambda t: t[2:] if t.startswith('n:') else t
            for i in range(c,d):
                nearby = expected[a+i-c:a+i-c+1] if b-a == d-c else expected[a:b]
                hints[i] = 'Ground truth' + ('' if len(nearby)==1 else ' in this section') + ': ' + ' '.join(map(display,nearby))
    for i, token in enumerate(actual):
        if not matched[i] and remaining[token] > 0:
            matched[i] = True
            remaining[token] -= 1
    spans = []
    for i, origin in enumerate(mapped):
        if origin:
            spans.append({'start':origin[0], 'end':origin[1], 'correct':matched[i],
                          'hint': 'Matches ground-truth content.' if matched[i] else hints[i]})
    spans.sort(key=lambda s:(s['start'],s['end']))
    merged = []
    for span in spans:
        if merged and span['start'] < merged[-1]['end']:
            prior = merged[-1]
            prior['end'] = max(prior['end'],span['end'])
            was_correct = prior['correct']
            prior['correct'] = prior['correct'] and span['correct']
            if not span['correct'] and was_correct:
                prior['hint'] = span['hint']
            elif not span['correct'] and span['hint'] not in prior['hint']:
                prior['hint'] += '\n' + span['hint']
        else:
            merged.append(span.copy())
    # Keep Python offsets independent of JavaScript's UTF-16 offsets by emitting text chunks.
    chunks, position = [], 0
    for span in merged:
        if position < span['start']:
            chunks.append({'text':candidate[position:span['start']], 'kind':'neutral'})
        chunks.append({'text':candidate[span['start']:span['end']],
                       'kind':'correct' if span['correct'] else 'incorrect', 'hint':span['hint']})
        position = span['end']
    if position < len(candidate):
        chunks.append({'text':candidate[position:], 'kind':'neutral'})
    assert ''.join(c['text'] for c in chunks) == candidate
    return chunks
