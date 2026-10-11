"""Read-only forensics of the saved live run. No retrieval/model replay or score.

Run from this checkout with venv/bin/python. SQLite is opened immutable/read-only
only after checking there is no WAL. Source, journal and database hashes are
checked before and after inspection. Only the diagnostic JSON is written.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from memory.mrag.corpus import _structured_position

RUN = Path('/tmp/helix-live-20261010-misw_7t0')
BEFORE = Path('/tmp/helix-attention-20261010-mox8f0hi/before')
OLD_AUDIT = ROOT / 'documents/audits/2026-10-10-live-agent'
OUT = Path(__file__).parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def read_database(path):
    assert not Path(str(path) + '-wal').exists(), 'Review WAL before immutable read'
    connection = sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def main():
    evidence = json.loads((OLD_AUDIT / 'evidence-locations.json').read_text())
    for item in evidence['files'].values():
        assert sha(Path(item['path'])) == item['sha256'], item['path']
    composition = json.loads((OLD_AUDIT / 'composition-manifest.json').read_text())
    sources = {}
    for name in ('helix', 'mightymem'):
        info = composition[name]
        for relative, expected in info['files'].items():
            current = Path(info['root']) / relative
            recorded = BEFORE / relative if name == 'helix' and (BEFORE / relative).exists() else current
            assert sha(recorded) == expected, (name, relative)
            sources[str(current)] = sha(current)

    checkpoint = RUN / 'data/mindscape/joint/checkpoint-000008'
    checkpoint_manifest = json.loads((checkpoint / 'manifest.json').read_text())
    native_path = checkpoint / 'mind.sqlite'
    assert sha(native_path) == checkpoint_manifest['files']['mind.sqlite']
    loom_path = RUN / 'data/mindscape/loom.sqlite'
    journal_path = RUN / 'data/memory/cognitive_journal.jsonl'
    protected = [RUN / 'trace.jsonl', RUN / 'data/mindscape/receipts.jsonl',
                 journal_path, loom_path, native_path]
    hashes = {str(path): sha(path) for path in protected}

    trace = read_rows(RUN / 'trace.jsonl')
    contexts = [r for r in read_rows(RUN / 'data/mindscape/receipts.jsonl') if r['kind'] == 'pulse_context']
    injections = [r for r in trace if r.get('function') == 'inject']
    foreground = [r for r in trace if r.get('function') == '_send_via_package']
    pulse_returns = [r for r in trace if r.get('function') == '_pulse']
    journal = read_rows(journal_path)
    loom = read_database(loom_path)
    native = read_database(native_path)
    try:
        records = {r['id']: dict(r) for r in loom.execute('SELECT * FROM records')}
        by_source = {json.loads(r['metadata'])['helix_source_id']: r for r in records.values()}
        native_records = {r['record_id']: dict(r) for r in native.execute('SELECT * FROM records')}
        legacy_messages = []
        legacy_scope = []
        for ordinal, row in enumerate(journal):
            if row['type'] != 'memory':
                continue
            meta = row.get('metadata') or {}
            source_id = meta.get('point_id') or f"mem_{row['id']}"
            when = meta.get('created_at') or row['timestamp']
            scope, turn, _, _ = _structured_position(row['content'], meta.get('tags', []), when, row.get('pulse_id', 0))
            if scope == '2026-06-30':
                legacy_scope.append({'id': source_id, 'turn': turn, 'created_at': when, 'ordinal': ordinal})
            if row['content'].startswith('[Message from '):
                projected = by_source[source_id]
                envelope = json.loads(projected['metadata']).get('record_envelope', {})
                legacy_messages.append({'id': source_id, 'created_at': when,
                    'canonical_kind': envelope.get('record_kind'),
                    'loom_kind': projected['kind'], 'loom_evidence_status': projected['evidence_status']})

        legacy_scope.sort(key=lambda r: (r['turn'], r['created_at'], r['ordinal']))
        # Read the actual checked source constant, not a new test/product limit.
        import ast
        module = ast.parse((ROOT / 'core/context_office.py').read_text())
        office_class = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'ContextOffice')
        scope_limit = next(ast.literal_eval(n.value) for n in office_class.body
                           if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MAX_SCOPE_ITEMS' for t in n.targets))
        subset = legacy_scope[:scope_limit]
        assert subset[-1]['id'] == 'mem_10'

        pulses = []
        previous_injection_time = 0
        for context, injection, returned in zip(contexts, injections, pulse_returns, strict=True):
            pulse = context['helix_pulse']
            packet = context['loom_packet']
            calls = [r for r in foreground if r['locals']['messages'][-1].get('content') == packet['rendered']]
            assert len(calls) == 1
            call = calls[0]
            assert call['result'] == returned['locals']['thought']
            manifest = packet['manifest']
            classifications = Counter()
            accepted = []
            for entry in manifest:
                for rid in entry['source_record_ids']:
                    record = records[rid]
                    metadata = json.loads(record['metadata'])
                    envelope = metadata.get('record_envelope') or {}
                    classifications[(entry['admitted'], record['kind'], envelope.get('record_kind', 'belief/no envelope'))] += 1
                    if entry['admitted']:
                        accepted.append({'id': metadata['helix_source_id'], 'kind': record['kind'],
                            'content_sha256': hashlib.sha256(record['content'].encode()).hexdigest(),
                            'lane_scores': entry['lanes'], 'reason': entry['reason']})

            native_selected = context['graph_trace']['selected_record_ids']
            absent_ids = [rid for rid in native_selected if rid not in records]
            assert all(rid in native_records for rid in absent_ids)
            annotations = '\n'.join(injection['result'][0])
            retrieval_calls = [r for r in trace if r.get('function') == 'retrieve'
                               and previous_injection_time < r['time'] < injection['time']]
            previous_injection_time = injection['time']
            mrag_rows = []
            for retrieval in retrieval_calls:
                for item in retrieval['result']:
                    mrag_rows.append({'id': item['id'], 'kind': item.get('record_kind'),
                        'created_at': item.get('created_at'), 'office_role': item.get('office_role'),
                        'office_scope': item.get('office_scope'), 'office_verified': item.get('office_verified'),
                        'full_body_in_preconscious_annotations': item['content'] in annotations})

            bypassed_private = []
            for entry in manifest:
                if entry['reason'] != 'private thought is not language-visible evidence':
                    continue
                for rid in entry['source_record_ids']:
                    record = records[rid]
                    sid = json.loads(record['metadata'])['helix_source_id']
                    if record['content'] in packet['current_input']:
                        assert any(r['id'] == sid and r['full_body_in_preconscious_annotations'] for r in mrag_rows)
                        bypassed_private.append(sid)

            output_text = '[response] ' + returned['locals']['thought']
            output_records = [r for r in records.values() if r['content'] == output_text]
            assert len(output_records) == 1
            output = output_records[0]
            source_id = json.loads(output['metadata'])['helix_source_id']
            later_admissions = [r['helix_pulse'] for r in contexts if r['helix_pulse'] > pulse
                and any(m['admitted'] and output['id'] in m['source_record_ids'] for m in r['loom_packet']['manifest'])]
            if pulse < len(contexts):
                assert injections[pulse]['locals']['previous_thought'] == returned['locals']['thought'][-500:]
            co = context['mrag'].get('context_office', {})
            pulses.append({'pulse': pulse, 'packet_id': packet['id'],
                'actual_foreground_call_matched': True,
                'current_events_in_prompt': all(ev in packet['rendered'] for ev in context['events']),
                'rwkv_state_changed': context['joint_state_before'] != context['joint_state_after'],
                'rwkv_event_tokens': context['rwkv_tokens'],
                'loom_candidate_count': len(manifest), 'loom_admitted': accepted,
                'loom_rejections': dict(Counter(m['reason'] for m in manifest if not m['admitted'])),
                'candidate_classifications': [dict(admitted=k[0], loom_kind=k[1], canonical_kind=k[2], count=v)
                                             for k,v in classifications.items()],
                'native_recalled_ids_without_loom_records': absent_ids,
                'mrag_returns': mrag_rows,
                'private_thought_ids_rejected_by_loom_but_present_in_prepacked_input': bypassed_private,
                'office': {k:co.get(k) for k in ('binding_method','scope','scope_coverage','verified','reason')},
                'stored_output_id': source_id, 'output_recalled_by_loom_on_pulses': later_admissions,
                'next_retrieval_query_includes_this_output_tail': pulse < len(contexts),
                'provider_receipt': {k:call['locals']['response'].get(k) for k in
                    ('model','done_reason','prompt_eval_count','eval_count')}})

        observed = json.loads((OLD_AUDIT / 'verification.json').read_text())
        old_state = by_source['mem_17']
        old_value = json.loads(old_state['content'].partition('] ')[2])['s_total']
        fresh_state_events = [match.group(1) for event in contexts[-1]['events']
            if (match := re.match(r'^\[\d{2}:\d{2}:\d{2}\] \[stability_drift\] (.*)$', event))]
        latest_state = ast.literal_eval(fresh_state_events[-1])
        answer_state_lines = [line.strip() for line in pulse_returns[-1]['locals']['thought'].splitlines()
                              if '`s_total` is climbing toward' in line]
        assert old_value == 2.898 and latest_state['s_total'] == 1.912
        assert len(answer_state_lines) == 1 and '**2.9**' in answer_state_lines[0]
        report = {
            'kind': 'read-only forensic diagnosis of recorded live integration; no new product evaluation',
            'new_product_result': None, 'runtime_source_edits_this_diagnosis': [],
            'recorded_run': str(RUN),
            'source_parity': {'recorded_sources_verified': True,
                             'pre_header_backups_used_for': ['core/pulse_loop.py','core/mindscape.py'],
                             'source_hashes_at_diagnosis': sources},
            'protected_evidence_hashes': hashes,
            'legacy_human_message_classifications': legacy_messages,
            'state_desk_ordering': {'scope': '2026-06-30', 'scope_record_count': len(legacy_scope),
                'inherited_MAX_SCOPE_ITEMS': scope_limit, 'truncated_prefix': subset,
                'labeled_current_after_prefix_reversal': subset[-1],
                'latest_by_production_chronology': legacy_scope[-1]},
            'pulses': pulses,
            'observed_temporal_error': {
                'old_source_record': 'mem_17', 'old_record_s_total': old_value,
                'old_record_created_at_epoch': old_state['created_at'],
                'retrieved_on_pulse': 3, 'answer_pulse': 4,
                'latest_received_s_total': latest_state['s_total'],
                'actual_answer_excerpt': answer_state_lines[0],
                'scope': 'contradiction visible in recorded input and output, not a benchmark score'},
            'native_feedback_tables': {table:native.execute('SELECT count(*) FROM '+table).fetchone()[0]
                for table in ('experience_cycles','experience_cycle_returns','outcomes')},
            'observed_action_route': {k:observed[k] for k in
                ('all_observed_tool_receipts','all_observed_native_motor_calls','all_observed_test_file_opens','requested_output_exists')},
            'interpretation_boundary': 'Presence and exact source matches prove exposure and persistence, not isolated causation of model behavior. Candidate/admission counts are diagnostics, not recall accuracy.'
        }
    finally:
        loom.close()
        native.close()
    assert hashes == {str(path): sha(path) for path in protected}, 'Saved evidence changed'
    assert all(sha(Path(path)) == digest for path,digest in sources.items()), 'Runtime source changed'
    report['saved_evidence_unchanged_after_inspection'] = True
    report['runtime_source_unchanged_after_inspection'] = True
    (OUT / 'memory-pathways.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'verified_pulses':len(pulses), 'legacy_human_messages':len(legacy_messages),
        'private_bypass':{p['pulse']:p['private_thought_ids_rejected_by_loom_but_present_in_prepacked_input'] for p in pulses},
        'saved_evidence_unchanged':True, 'runtime_source_edits':[], 'new_product_result':None},indent=2))


if __name__ == '__main__':
    main()
