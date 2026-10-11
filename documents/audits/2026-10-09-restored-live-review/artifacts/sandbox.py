"""Mount isolated normal Helix state paths and execute its unchanged entry points."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

RUN = Path(__file__).resolve().parent
M = json.loads((RUN / 'manifest.json').read_text())
ROOT = Path(M['root'])
for name, digest in M['source_hashes'].items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
        raise RuntimeError(f'Source changed since composition capture: {name}')

mode = sys.argv[1]
env = {k: v for k, v in os.environ.items()
       if k in {'HOME', 'USER', 'LOGNAME', 'PATH', 'LANG', 'LC_ALL', 'TERM', 'LD_LIBRARY_PATH'}}
env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1',
           HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
           TMPDIR=str(RUN / 'temporary'))
(RUN / 'temporary').mkdir(exist_ok=True)
command = ['bwrap', '--die-with-parent', '--ro-bind', '/', '/', '--dev', '/dev',
           '--proc', '/proc', '--bind', str(RUN), str(RUN)]
for folder in ('data', 'logs', 'journals', 'config'):
    command += ['--bind', str(RUN / folder), str(ROOT / folder)]
command += ['--bind', str(RUN / 'credentials'), str(Path.home() / '.config/helix'),
            '--chdir', str(ROOT)]
if mode == 'setup':
    args = [str(ROOT/'venv/bin/python'), 'setup.py', '--non-interactive', '--local-mode',
            '--provider', 'ollama', '--model', 'granite4.1:3b', '--agent-name', 'Helix',
            '--creator-name', 'User', '--profile', 'standard', '--personality', 'curious']
elif mode in ('agent', 'agent-active'):
    env['PYTHONPATH'] = str(RUN/'observer') + os.pathsep + str(ROOT)
    env['HELIX_REVIEW_TRACE'] = str(RUN/'evidence/trace.jsonl')
    if mode == 'agent-active':
        env['HELIX_TASK_COGNITION'] = 'active'
    args = [str(ROOT/'venv/bin/python'), 'main.py']
elif mode == 'dashboard':
    args = [str(ROOT/'venv/bin/python'), 'dashboard/dashboard.py', '--host', '127.0.0.1', '--port', '15050']
else:
    raise ValueError(mode)
command += ['--', *args]
(RUN/'evidence'/f'{mode}-command.json').write_text(json.dumps({
    'command': command, 'environment_keys': sorted(env), 'source_parity': True,
    'entrypoint_unchanged': True}, indent=2)+'\n')
if mode == 'setup':
    with (RUN/'evidence/setup.log').open('w') as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    print((RUN/'evidence/setup.log').read_text())
    print('SETUP_EXIT', result.returncode)
    sys.exit(result.returncode)
os.execvpe(command[0], command, env)
