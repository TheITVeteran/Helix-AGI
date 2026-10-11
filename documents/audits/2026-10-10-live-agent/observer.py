"""Passive function-return observer; never changes arguments, results or routing."""
import dataclasses
import json
import os
import sys
import threading
import time

_path = os.environ.get('HELIX_REVIEW_TRACE')
_lock = threading.Lock()
_targets = {
    ('llm/providers/base.py', 'detect_available_provider'): (),
    ('memory/memory_manager.py', 'store'): ('content', 'tags', 'metadata'),
    ('core/preconscious.py', 'inject'): ('incoming_events', 'previous_thought'),
    ('core/unified_retrieval.py', 'retrieve'): ('query',),
    ('llm/providers/ollama_provider.py', '_send_via_package'): ('messages', 'response'),
    ('llm/providers/ollama_provider.py', 'send_message'): ('message',),
    ('tools/tool_executor.py', 'execute_function_call_receipt'): ('name', 'args'),
    ('tools/channel_router.py', 'route_reply'): ('recipient', 'message'),
    ('core/pulse_loop.py', '_pulse'): ('events', 'pulse_message', 'thought'),
    ('llm/orchestrated.py', 'send_message'): ('message', 'thought', 'result'),
    ('core/curator.py', '_run_nightly_cycle'): (),
    ('core/task_cognition/controller.py', '__init__'): ('requested', 'tool_capable', 'standard_loop'),
    ('habitus_ai/sensory_motor_loop.py', 'run_turn'): ('user_input', 'target_path'),
    ('main.py', 'poll_dashboard'): (),
    ('core/mindscape.py', 'classify_sensed_feeling'): ('events',),
    ('core/pulse_loop.py', '_deliver_mindscape_output'): ('thought','events','feeling','clean_text','recipient','channel','delivered'),
    ('dashboard/dashboard_comms.py', 'push_outbound'): ('recipient','message'),
    ('habitus_ai/developmental_runtime.py', 'actualize'): ('authorization',),
}

def _encode(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (tuple, list)):
        return [_encode(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _encode(v) for k, v in value.items()}
    if hasattr(value, 'model_dump'):
        return _encode(value.model_dump())
    if dataclasses.is_dataclass(value):
        return _encode(dataclasses.asdict(value))
    if type(value).__name__ == 'ProviderConfig':
        return {k: _encode(getattr(value, k, None)) for k in
                ('provider_type', 'model', 'context_window', 'max_output_tokens', 'options')}
    if hasattr(value, 'tolist'):
        return _encode(value.tolist())
    return {'type': type(value).__name__}

def _observe(frame, event, arg):
    if event != 'return':
        return
    filename = frame.f_code.co_filename.replace('\\', '/')
    for (suffix, name), keys in _targets.items():
        if frame.f_code.co_name != name or not filename.endswith('/'+suffix):
            continue
        item = {'time': time.time(), 'thread': threading.current_thread().name,
                'source': suffix, 'function': name, 'result': _encode(arg),
                'locals': {k: _encode(frame.f_locals[k]) for k in keys if k in frame.f_locals}}
        obj = frame.f_locals.get('self')
        if hasattr(obj, 'model') and isinstance(obj.model, str):
            item['model'] = obj.model
        if suffix == 'core/task_cognition/controller.py':
            item['effective_mode'] = getattr(obj, 'mode', None)
        with _lock:
            with open(_path, 'a') as output:
                output.write(json.dumps(item, ensure_ascii=False)+'\n')
        break

if _path:
    sys.setprofile(_observe)
    threading.setprofile(_observe)
    def _audit(event, args):
        if event == 'open' and args and 'sensory-room/' in str(args[0]):
            with _lock:
                with open(_path, 'a') as output:
                    output.write(json.dumps({'time': time.time(), 'source': 'python audit',
                        'function': event, 'result': 'attempt only; emitted before syscall',
                        'args': _encode(args)})+'\n')
    sys.addaudithook(_audit)
