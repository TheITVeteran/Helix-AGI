"""Preserve observed evidence, without filling in missing product results."""
import hashlib,json,shutil,time
from pathlib import Path
run=Path(__file__).parent
root=Path('/home/nemo/Helix_AGI (GitHub Repo) (Public)')
audit=root/'documents/audits/2026-10-10-operational-recheck'
audit.mkdir(parents=True,exist_ok=True)
def lines(path):
    values=[]
    for line in path.read_text().splitlines() if path.exists() else []:
        try: values.append(json.loads(line))
        except json.JSONDecodeError: pass
    return values
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
manifest=json.loads((run/'composition-manifest.json').read_text())
trace=lines(run/'trace.jsonl')
native=[e for e in lines(run/'data/mindscape/receipts.jsonl') if e.get('time',0)>=manifest['created']]
journal=lines(run/'data/memory/cognitive_journal.jsonl')
outputs=json.loads((run/'data/dashboard_messages.json').read_text()).get('outbound',[])
cases=[]
for name in ['conversation','sense','read','script']:
    request=json.loads((run/(name+'.request.json')).read_text())
    contexts=[e for e in native if e.get('kind')=='pulse_context' and any(request['content'] in event for event in e.get('events',[]))]
    item={'case':name,'request':request,'context_found':bool(contexts)}
    directory=audit/'cases'/name;directory.mkdir(parents=True,exist_ok=True)
    if contexts:
        context=contexts[-1];pulse=context['helix_pulse'];packet=context['loom_packet']
        foreground=[e for e in native if e.get('kind')=='foreground_return' and e.get('helix_pulse')==pulse]
        provider=[e for e in trace if e.get('function')=='_send_via_package' and e.get('thread')=='helix_pulse' and e.get('time',0)>context['time'] and foreground and e['time']<=foreground[-1]['time']]
        delivered=[e for e in outputs if foreground and e.get('content')==foreground[-1].get('thought') and e.get('timestamp',0)>=context['time']]
        ingestion=[e for e in journal if request['content'] in e.get('content','')]
        item.update(pulse=pulse,ingestion_ids=[e.get('id') for e in ingestion],provider_found=bool(provider),outward_reply=delivered[-1:] or None)
        if provider:
            response=provider[-1]['locals']['response']
            item['generation']={k:response.get(k) for k in ['model','done','done_reason','prompt_eval_count','eval_count']}
            item['exact_packet_in_provider_request']=any(e.get('content')==packet['rendered'] for e in provider[-1]['locals']['messages'])
        item['context_packet_id']=packet['id']
        for filename,value in [('context.json',context),('foreground.json',foreground),('provider.json',provider),('delivered.json',delivered),('ingestion.json',ingestion)]:
            (directory/filename).write_text(json.dumps(value,indent=2))
        (directory/'context.txt').write_text(packet['rendered'])
    cases.append(item)
canonical=json.loads((run/'canonical-before.json').read_text())
changed=[name for name,value in canonical.items() if not (root/name).is_file() or digest(root/name)!=value]
added=[str(p.relative_to(root)) for d in ['data','config'] for p in (root/d).rglob('*') if p.is_file() and str(p.relative_to(root)) not in canonical]
actions=[e for e in trace if e.get('function') in ['actualize','run_turn','execute_function_call_receipt']]
file_attempts=[e for e in trace if e.get('function')=='open']
verification={'created':time.time(),'kind':'unscored current product operational diagnosis','full_product_result':None,
    'case_count':len(cases),'current_inputs_persisted':all(e.get('ingestion_ids') for e in cases),
    'exact_packets_reached_provider':all(e.get('exact_packet_in_provider_request') for e in cases),
    'action_receipt_count':len(actions),'workspace_file_open_attempt_count':len(file_attempts),
    'script_exists':(run/'sensory-room/output/inventory.py').exists(),
    'workspace':{str(p.relative_to(run)): {'sha256':digest(p),'bytes':p.stat().st_size} for p in (run/'sensory-room').rglob('*') if p.is_file()},
    'canonical_checked_files':len(canonical),'canonical_changed':changed,'canonical_added':added,
    'source_changes_during_run':{name:[p for p,h in manifest[name]['files'].items() if digest(Path(manifest[name]['root'])/p)!=h] for name in ['helix','mightymem']},
    'wake_observations':[e for e in trace if e.get('function')=='wake'],
    'stop_receipt':json.loads((run/'stop-receipt.json').read_text()) if (run/'stop-receipt.json').exists() else None}
(audit/'observed-cases.json').write_text(json.dumps(cases,indent=2))
(audit/'verification.json').write_text(json.dumps(verification,indent=2))
for name in ['composition-manifest.json','host-runtime.json','wizard-ui.jsonl','trace.jsonl','interactions.jsonl','wizard-console.log','run.sh','sequence.py','sequence.log','client.py','stop-receipt.json','collect.py']:
    if (run/name).exists():shutil.copy2(run/name,audit/name)
for name in ['launcher.log','bootstrap.log','helix.log']:
    if (run/'logs'/name).exists():shutil.copy2(run/'logs'/name,audit/name)
for name in ['sitecustomize.py','wizard_driver.py']:shutil.copy2(run/'observer'/name,audit/name)
shutil.copy2(run/'data/mindscape/composition-manifest.json',audit/'runtime-composition.json')
(audit/'runtime-receipts.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in native))
print(json.dumps({'cases':cases,'verification':verification},indent=2))
