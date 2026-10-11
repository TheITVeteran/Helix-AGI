"""Drive requested user turns through the real dashboard; never author outputs."""
import json,time,urllib.request
from pathlib import Path
run=Path(__file__).parent
cases=['conversation','sense','read','script']
for index,case in enumerate(cases):
    request=json.loads((run/(case+'.request.json')).read_text())
    if index:
        payload=json.dumps(request).encode()
        response=json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5050/api/messages',data=payload,headers={'Content-Type':'application/json'})))
        with (run/'interactions.jsonl').open('a') as out:out.write(json.dumps({'case':case,'submitted_at':time.time(),'request':request,'http_response':response})+'\n')
        print('Submitted '+case,flush=True)
    while True:
        matches=[]
        if (run/'trace.jsonl').exists():
            for line in (run/'trace.jsonl').read_text().splitlines():
                try:entry=json.loads(line)
                except json.JSONDecodeError:continue
                if entry.get('function')=='_pulse' and any(request['content'] in value for value in entry.get('locals',{}).get('events',[])):matches.append(entry)
        manifest_path=run/'data/mindscape/composition-manifest.json'
        if manifest_path.exists() and json.loads(manifest_path.read_text()).get('status')=='failed':
            raise SystemExit('Agent failed explicitly; preserve receipts and diagnose.')
        if matches:
            print(json.dumps({'case':case,'pulse_finished':matches[-1]['time'],'thought':matches[-1].get('locals',{}).get('thought')}),flush=True)
            break
        time.sleep(2)
(run/'stop-receipt.json').write_text(json.dumps({'time':time.time(),'reason':'all four requested test turns returned; normal wizard close requested'},indent=2))
(run/'close-wizard').write_text('Close after the requested case turns.\n')
