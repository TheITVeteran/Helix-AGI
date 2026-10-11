import json,time,urllib.request,sys
from pathlib import Path
run=Path(__file__).parent
if len(sys.argv)>1:
 case=sys.argv[1]; payload=json.loads((run/(case+'.request.json')).read_text())
 req=urllib.request.Request('http://127.0.0.1:5050/api/messages',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 response=json.load(urllib.request.urlopen(req))
 receipt={'case':case,'submitted_at':time.time(),'request':payload,'http_response':response}
else:
 response=json.load(urllib.request.urlopen('http://127.0.0.1:5050/api/messages/outbound'))
 receipt={'observed_at':time.time(),'http_outbound':response}
with (run/'interactions.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
display = dict(receipt)
if 'http_outbound' in display:
 display['http_outbound'] = {'total': response['total'], 'latest_message': response['messages'][-1:] }
print(json.dumps(display,indent=2))
