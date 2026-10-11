"""Summarize receipts from the actual wizard/agent run; never invent outputs."""
from pathlib import Path
import collections,hashlib,json,shutil,time
run=Path(__file__).parent
root=Path('/home/nemo/Helix_AGI (GitHub Repo) (Public)')
audit=root/'documents/audits/2026-10-10-wizard-live'
def load_lines(p):
 out=[]
 for line in p.read_text().splitlines():
  try:out.append(json.loads(line))
  except json.JSONDecodeError:continue
 return out
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
manifest=json.loads((run/'composition-manifest.json').read_text());start=manifest['created']
trace=load_lines(run/'trace.jsonl');native=[e for e in load_lines(run/'data/mindscape/receipts.jsonl') if e.get('time',0)>=start]
journal=load_lines(run/'data/memory/cognitive_journal.jsonl');interactions=load_lines(run/'interactions.jsonl')
communication=json.loads((run/'data/dashboard_messages.json').read_text()) if (run/'data/dashboard_messages.json').exists() else None
if communication is None:
 candidates=list((run/'data').rglob('*comms*.json'));print('Communication candidates',candidates)
 raise SystemExit('Find actual dashboard state before collecting results')
outputs=communication['outbound']
actions=[e for e in trace if e['function'] in ['execute_function_call_receipt','actualize','run_turn']]
file_attempts=[e for e in trace if e['function']=='open']
case_results=[]
for case in ['conversation','correction','sense','read','script']:
 req=json.loads((run/(case+'.request.json')).read_text());content=req['content']
 pcs=[d for d in native if d['kind']=='pulse_context' and any(content in s for s in d['events'])]
 assert len(pcs)==1,(case,len(pcs))
 context=pcs[0];pulse=context['helix_pulse']
 foreground=next(e for e in native if e['kind']=='foreground_return' and e['helix_pulse']==pulse)
 response=next(e for e in trace if e['function']=='_send_via_package' and e['thread']=='helix_pulse' and e['time']>=context['time'] and e['time']<=foreground['time'] and e['result']==foreground['thought'])
 delivered=next(e for e in outputs if e['content']==foreground['thought'] and e['timestamp']>=response['time'])
 journal_matches=[e for e in journal if content in e.get('content','')]
 records=[{k:e.get(k) for k in ['id','type','timestamp','content','metadata']} for e in journal_matches]
 raw=response['locals']['response'];requests=response['locals']['messages']
 packet=context['loom_packet'];packet_text=packet['rendered']
 case_dir=audit/'cases'/case;case_dir.mkdir(parents=True,exist_ok=True)
 (case_dir/'context-receipt.json').write_text(json.dumps(context,indent=2))
 (case_dir/'provider-receipt.json').write_text(json.dumps(response,indent=2))
 (case_dir/'delivered-reply.json').write_text(json.dumps(delivered,indent=2))
 (case_dir/'ingestion.json').write_text(json.dumps({'http_submission':next(x for x in interactions if x.get('case')==case),'persistent_journal_records':records},indent=2))
 (case_dir/'rendered-context.txt').write_text(packet_text)
 item={'case':case,'pulse':pulse,'request':req,'persistent_input_ids':[e['id'] for e in journal_matches],
       'rwkv_tokens':context['rwkv_tokens'],'state_before':context['joint_state_before'],'state_after':context['joint_state_after'],
       'loom_packet_id':packet['id'],'configured_lanes':json.loads((run/'data/mindscape/composition-manifest.json').read_text())['runtime']['loom_lanes'],
       'contributing_lanes':sorted(set(k for e in packet['manifest'] for k in e.get('lanes',{}))),
       'mrag':context['mrag'],'exact_compiled_packet_in_model_request':any(m['content']==packet_text for m in requests),
       'current_request_in_model_request':any(content in m['content'] for m in requests),
       'generation':{k:raw.get(k) for k in ['model','done','done_reason','prompt_eval_count','eval_count']},
       'delivered':delivered,'receipt_directory':str(case_dir.relative_to(audit))}
 case_results.append(item)
assert not (run/'sensory-room/output/inventory.py').exists(), 'Agent created an output: inspect and verify it before reporting.'
actual={str(p.relative_to(run)): {'sha256':digest(p),'bytes':p.stat().st_size} for p in (run/'sensory-room').rglob('*') if p.is_file()}
canonical_before=json.loads((run/'canonical-before.json').read_text());changed=[p for p,h in canonical_before.items() if not (root/p).is_file() or digest(root/p)!=h]
new_canonical=[str(p.relative_to(root)) for d in ['data','config'] for p in (root/d).rglob('*') if p.is_file() and str(p.relative_to(root)) not in canonical_before]
source_changes={name:[p for p,h in manifest[name]['files'].items() if digest(Path(manifest[name]['root'])/p)!=h] for name in ['helix','mightymem']}
verification={'created':time.time(),'kind':'unscored live diagnosis; no full-system readiness result','case_count':len(case_results),
 'wizard':{'actual_ui_trace':'wizard-ui.jsonl','dependencies_exit':0,'bootstrap_return':True,'normal_main_child':1751151,'display':'real Qt widgets on offscreen platform; physical desktop/WebGL rendering not validated'},
 'foreground_generation_ends':[e['generation']['done_reason'] for e in case_results],
 'current_requests_reached_model':all(e['current_request_in_model_request'] for e in case_results),
 'all_inputs_persisted':all(e['persistent_input_ids'] for e in case_results),
 'action_receipt_count':len(actions),'workspace_python_open_attempt_count':len(file_attempts),
 'inventory_script_exists':False,'workspace':actual,'input_hashes_unchanged':all(actual[p]['sha256']==h for p,h in manifest['input_files'].items()),
 'expected_read_facts':{'archive_label':'LANTERN-482','inspection_day':'Tuesday','survey_reference':'PEARL-619','shelves':5},
 'canonical_checked_files':len(canonical_before),'canonical_changed':changed,'canonical_added':new_canonical,'product_source_changes_during_run':source_changes,
 'stop_receipt':json.loads((run/'stop-receipt.json').read_text()) if (run/'stop-receipt.json').exists() else None}
(audit/'observed-cases.json').write_text(json.dumps(case_results,indent=2));(audit/'verification.json').write_text(json.dumps(verification,indent=2))
for p in ['wizard-ui.jsonl','trace.jsonl','interactions.jsonl','wizard-console.log','run.sh','client.py','stop_after_script_turn.py','stop-receipt.json','dependency-preflight.txt','host-runtime.json','ollama-boundary.log']:
 if (run/p).exists():shutil.copy2(run/p,audit/p)
shutil.copy2(run/'observer/sitecustomize.py',audit/'observer.py');shutil.copy2(run/'observer/wizard_driver.py',audit/'wizard_driver.py')
shutil.copy2(run/'screenshots/page-6.png',audit/'wizard-review.png')
for p in ['launcher.log','bootstrap.log','helix.log']:shutil.copy2(run/'logs'/p,audit/p)
(audit/'runtime-receipts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in native))
shutil.copy2(run/'data/mindscape/composition-manifest.json',audit/'runtime-composition.json')
(audit/'artifact-hashes.json').write_text(json.dumps({str(p.relative_to(audit)):digest(p) for p in audit.rglob('*') if p.is_file() and p.name!='artifact-hashes.json'},indent=2))
print(json.dumps(verification,indent=2))
