"""End this requested trial after the actual script-request pulse finishes."""
import json,time
from pathlib import Path
r=Path(__file__).parent
request=json.loads((r/'script.request.json').read_text())['content']
while True:
    for line in (r/'trace.jsonl').read_text().splitlines():
        try: event=json.loads(line)
        except json.JSONDecodeError: continue
        if event.get('function')=='_pulse' and any(request in text for text in event.get('locals',{}).get('events',[])):
            (r/'stop-receipt.json').write_text(json.dumps({'time':time.time(),'reason':'all five requested live turns completed; script request pulse returned','matching_observer_event':event['time']},indent=2))
            (r/'close-wizard').write_text('Close through the real wizard closeEvent after final requested turn.\n')
            print('Final requested pulse completed; requested graceful close through the wizard.',flush=True)
            raise SystemExit(0)
    time.sleep(1)
