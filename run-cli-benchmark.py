#!/usr/bin/env python3
"""Run independent visual extraction requests using installed agy, llm, or codex."""
import argparse
import concurrent.futures
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
CONFIGS = {
    'agy': [(f'gemini-3.8-flash-{effort}', f'gemini-3.8-flash-{effort}', effort)
            for effort in ('low', 'medium', 'high')],
    'llm': [(f'claude-{family}-5.5', f'anthropic/claude-{family}-5-5', None)
            for family in ('opus', 'haiku', 'sonnet')] +
           [(f'qwen{variant}', f'openrouter/qwen/qwen{variant}', None)
            for variant in ('3.5-35b-a3b', '3.7-flash', '3.8-flash')],
    'codex': [(f'gpt-6.1-sol-{effort}', 'gpt-6.1-sol', effort)
              for effort in ('low', 'medium', 'high')] +
             [('gpt-6-astra-low-cli', 'gpt-6-astra', 'low')] +
             [(f'gpt-6-luna-{effort}-cli', 'gpt-6-luna', effort)
              for effort in ('low', 'medium', 'high')],
}

def codex_response(stdout, final_path):
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    completions = [e for e in events if e.get('type') == 'turn.completed']
    errors = [e for e in events if e.get('type') == 'turn.failed']
    if errors or not completions:
        raise ValueError('Codex did not complete a turn: ' + str(errors)[:500])
    content = final_path.read_text() if final_path.exists() else ''
    if not content.strip():
        raise ValueError('Codex returned no final extraction')
    usage = completions[-1].get('usage', {})
    return {'response': content, 'usage': usage,
            'raw_format': 'Normalized from retained Codex JSONL events and final message',
            'tool_items': [e['item'] for e in events if e.get('type') == 'item.completed'
                           and e.get('item', {}).get('type') not in ('agent_message', 'reasoning')]}

def now():
    return datetime.now(ZoneInfo('Europe/London')).isoformat()

def save_json(path, value):
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)

def load_prompts():
    instructions = (ROOT / 'agent-instructions.md').read_text()
    shared = instructions.split('## Shared extraction instruction\n\n', 1)[1].split('\n\n## Tasks', 1)[0]
    tasks = []
    for number, text in re.findall(r'^(\d+)\. (.+)$', instructions, re.M):
        filename = re.search(r'`([^`]+)`', text).group(1)
        prompt = text.replace('`', '') + '\n\n' + shared
        source = ROOT / 'files' / filename
        tasks.append({'task': int(number), 'input': 'files/' + filename,
                      'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'output': source.stem + '.md', 'prompt': prompt})
    assert len(tasks) == 8
    return instructions, tasks

def extract_response(stdout, backend):
    value = json.loads(stdout)
    if isinstance(value, list):
        candidates = [v for v in value if isinstance(v, dict) and v.get('type') == 'result']
        value = candidates[-1] if candidates else value[-1]
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON response object')
    if value.get('is_error'):
        raise ValueError('CLI returned is_error: ' + str(value.get('result', ''))[:500])
    if backend == 'agy' and value.get('status') not in (None, 'SUCCESS'):
        raise ValueError('agy returned status: ' + str(value['status']))
    for key in (('response',) if backend == 'llm' else ('result', 'response', 'text')):
        text = value.get(key)
        if isinstance(text, str) and text.strip():
            return text, value
    raise ValueError('Missing nonempty final response; top-level keys: ' + str(list(value)))

def llm_attachment(source, outdir):
    # Anthropic measures the encoded image against a 10 MiB limit.
    if 4 * ((source.stat().st_size + 2) // 3) <= 10 * 1024 * 1024:
        return source, None
    from PIL import Image
    target = outdir / 'raw' / 'inputs' / source.name
    target.parent.mkdir(exist_ok=True)
    with Image.open(source) as image:
        assert source.read_bytes()[24] == 8, 'Recompression must preserve original bit depth'
        original_pixels = image.tobytes()
        original_mode, original_size = image.mode, image.size
        if not target.exists():
            image.save(target, format='PNG', optimize=True, compress_level=9)
    with Image.open(target) as image:
        assert image.mode == original_mode and image.size == original_size
        assert image.tobytes() == original_pixels, 'Recompression changed decoded pixels'
    assert 4 * ((target.stat().st_size + 2) // 3) <= 10 * 1024 * 1024, 'Lossless attachment still exceeds provider limit'
    return target, {'method': 'Lossless PNG recompression with Pillow optimize=True, compress_level=9',
                    'reason': 'Original base64 payload exceeds Anthropic 10 MiB image limit',
                    'attachment': str(target.relative_to(outdir)),
                    'attachment_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                    'decoded_pixels_sha256': hashlib.sha256(original_pixels).hexdigest(),
                    'identical_decoded_pixels_verified': True,
                    'dimensions': list(original_size), 'mode': original_mode}

def run_config(backend, config, run_date, selected):
    dirname, model, effort = config
    instructions, tasks = load_prompts()
    outdir = ROOT / 'results' / dirname / run_date
    outdir.mkdir(parents=True, exist_ok=True)
    rawdir = outdir / 'raw'
    rawdir.mkdir(exist_ok=True)
    manifest = outdir / 'run.json'
    if manifest.exists():
        run = json.loads(manifest.read_text())
        by_id = {t['task']: t for t in run['tasks']}
        assert run['instructions_sha256'] == hashlib.sha256(instructions.encode()).hexdigest(), 'Instructions changed; use a new run directory'
        tasks = [by_id[t['task']] for t in tasks]
    else:
        run = {'model': model, 'reasoning_effort': effort or 'provider default (not overridden)',
               'backend': backend, 'date': run_date, 'started_at': now(),
               'instructions_sha256': hashlib.sha256(instructions.encode()).hexdigest(),
               'execution': 'Fresh CLI invocation per image; no conversation continuation, OCR, reference answers, or editorial corrections.',
               'reference_status': 'Ground truth is used only after extraction, never supplied to the model.',
               'tasks': tasks}
        (outdir / 'instructions.md').write_text(instructions)
    run['status'] = 'running'
    save_json(manifest, run)
    for task in tasks:
        if task['task'] not in selected or task.get('status') == 'completed':
            continue
        source = ROOT / task['input']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == task['input_sha256']
        stem = source.stem
        prompt = task['prompt']
        if task.get('status') == 'failed':
            previous = {k: v for k, v in task.items() if k not in ('previous_attempts', 'input', 'input_sha256', 'output', 'task', 'prompt')}
            attempt_id = len(task.get('previous_attempts', [])) + 1
            archive = rawdir / 'attempts'
            archive.mkdir(exist_ok=True)
            for key, suffix in [('raw_stdout', 'stdout.json'), ('raw_stderr', 'stderr.txt')]:
                old_file = outdir / task[key]
                if old_file.exists():
                    archived = archive / f'{stem}-attempt-{attempt_id}.{suffix}'
                    old_file.replace(archived)
                    previous[key] = str(archived.relative_to(outdir))
            task.setdefault('previous_attempts', []).append(previous)
            for key in ['error', 'exit_code', 'finished_at', 'elapsed_seconds']:
                task.pop(key, None)
        workspace = None
        if backend == 'agy':
            workspace = tempfile.TemporaryDirectory(prefix='extract-benchmark-agy-')
            # The fresh workspace contains only the one visual input.
            input_copy = Path(workspace.name) / source.name
            input_copy.write_bytes(source.read_bytes())
            prompt += ('\n\nThe sole visual input is ' + str(input_copy) +
                       '. Inspect this image visually exactly once, then return only the requested extraction.'
                       ' Do not read other files, use terminal tools, run OCR, perform Git operations,'
                       ' use other task results, or write files. Do not ask follow-up questions.')
            command = ['agy', '--model', model, '--mode', 'plan', '--disable-slash-commands',
                       '--output-format', 'json', '--print-timeout', '10m', '--print', prompt]
            cwd = workspace.name
        elif backend == 'codex':
            workspace = tempfile.TemporaryDirectory(prefix='extract-benchmark-codex-')
            prompt += ('\n\nThe visual input is attached to this request. Inspect it visually once.'
                       ' Return the extraction as your final response. Do not use tools, read files,'
                       ' run terminal commands, perform Git operations, write files, or ask questions.')
            final_path = Path(workspace.name) / 'final.md'
            command = ['codex', '--no-daemon', '-a', 'never', 'exec', '--ignore-user-config',
                       '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only',
                       '--model', model, '-c', f'model_reasoning_effort="{effort}"',
                       '--image', str(source), '--json', '--output-last-message', str(final_path), prompt]
            cwd = workspace.name
            task['raw_events'] = 'raw/' + stem + '.events.jsonl'
        else:
            attachment, preparation = llm_attachment(source, outdir) if model.startswith('anthropic/') else (source, None)
            if preparation:
                task['attachment_preparation'] = preparation
            command = ['llm', '-m', model, '-a', str(attachment), '--no-log', '--hide-reasoning', '--json', prompt]
            cwd = ROOT
        task.update({'status': 'running', 'started_at': now(), 'command': command,
                     'submitted_prompt': prompt, 'raw_stdout': 'raw/' + stem + '.stdout.json',
                     'raw_stderr': 'raw/' + stem + '.stderr.txt'})
        save_json(manifest, run)
        print(f'START {dirname} task {task["task"]} {source.name}', flush=True)
        start = time.monotonic()
        try:
            completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=660)
            (rawdir / (stem + '.stderr.txt')).write_text(completed.stderr)
            task['exit_code'] = completed.returncode
            if backend == 'codex':
                (outdir / task['raw_events']).write_text(completed.stdout)
                response_value = {'events_file': task['raw_events']}
                save_json(rawdir / (stem + '.stdout.json'), response_value)
                if completed.returncode == 0:
                    response_value = codex_response(completed.stdout, final_path)
                save_json(rawdir / (stem + '.stdout.json'), response_value)
            else:
                (rawdir / (stem + '.stdout.json')).write_text(completed.stdout)
            if completed.returncode:
                raise RuntimeError(f'CLI exit {completed.returncode}: {completed.stderr[-1000:]}')
            content, response = extract_response(json.dumps(response_value) if backend == 'codex' else completed.stdout, backend)
            output = outdir / task['output']
            output.write_text(content)
            task.update({'status': 'completed', 'output_bytes': output.stat().st_size,
                         'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
            for key in ('model', 'model_id', 'resolved_model', 'options_json', 'duration_ms', 'duration_api_ms', 'duration_seconds', 'usage', 'input_tokens', 'output_tokens', 'token_details', 'num_turns', 'session_id', 'conversation_id'):
                if key in response:
                    task.setdefault('response_metadata', {})[key] = response[key]
            # Anthropic stop reasons expose truncation without altering the response.
            provider = response.get('response_json', {})
            if isinstance(provider, dict) and provider.get('stop_reason'):
                task.setdefault('response_metadata', {})['stop_reason'] = provider['stop_reason']
            if isinstance(provider, dict) and provider.get('model'):
                task.setdefault('response_metadata', {})['provider_model'] = provider['model']
        except subprocess.TimeoutExpired as error:
            for suffix, data in (('stdout.json', error.stdout), ('stderr.txt', error.stderr)):
                if data is not None:
                    target = outdir / task['raw_events'] if backend == 'codex' and suffix == 'stdout.json' else rawdir / (stem + '.' + suffix)
                    target.write_bytes(data.encode() if isinstance(data, str) else data)
            task.update({'status': 'failed', 'error': 'CLI exceeded 660-second timeout'})
        except Exception as error:
            task.update({'status': 'failed', 'error': str(error)})
        finally:
            if workspace:
                workspace.cleanup()
        task.update({'finished_at': now(), 'elapsed_seconds': round(time.monotonic() - start, 3)})
        save_json(manifest, run)
        print(f'{task["status"].upper()} {dirname} task {task["task"]} ({task["elapsed_seconds"]}s)' +
              ((' ' + task['error'][:300]) if task.get('status') == 'failed' else ''), flush=True)
    statuses = [t.get('status', 'pending') for t in tasks]
    run['status'] = 'completed' if all(s == 'completed' for s in statuses) else ('incomplete' if 'failed' in statuses else 'partial')
    run['finished_at'] = now()
    save_json(manifest, run)
    return dirname, run['status'], sum(s == 'completed' for s in statuses)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('backend', choices=CONFIGS)
    parser.add_argument('--date', default=datetime.now(ZoneInfo('Europe/London')).date().isoformat())
    parser.add_argument('--models', nargs='*')
    parser.add_argument('--tasks', nargs='*', type=int, default=list(range(1, 9)))
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    configs = [c for c in CONFIGS[args.backend] if not args.models or c[0] in args.models]
    if not configs:
        parser.error('No matching model configurations')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_config, args.backend, c, args.date, args.tasks) for c in configs]
        for future in concurrent.futures.as_completed(futures):
            print('SUMMARY', *future.result(), flush=True)

if __name__ == '__main__':
    main()
