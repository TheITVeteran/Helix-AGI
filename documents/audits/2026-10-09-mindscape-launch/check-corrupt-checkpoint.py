from pathlib import Path
import hashlib, json, subprocess
run=Path(__file__).resolve().parent
pointer=run/'data/mindscape/joint/LATEST.json'
original=pointer.read_bytes()
payload=json.loads(original)
payload['manifest_sha256']='0'*64
try:
 pointer.write_text(json.dumps(payload))
 with (run/'corrupt-checkpoint.log').open('w') as log:
  result=subprocess.run(['bash',str(run/'check.sh')],stdout=log,stderr=subprocess.STDOUT)
 manifest=json.loads((run/'data/mindscape/composition-manifest.json').read_text())
 observed={'kind':'unscored startup integrity diagnostic','mutation':'corrupt the isolated latest pointer hash only','exit_code':result.returncode,'status':manifest['status'],'error':manifest.get('error')}
 assert result.returncode!=0 and 'checkpoint manifest hash mismatch' in observed['error'], observed
finally:
 pointer.write_bytes(original)
assert pointer.read_bytes()==original
observed['original_pointer_restored']=True
(run/'corrupt-checkpoint-result.json').write_text(json.dumps(observed,indent=2)+'\n')
print(json.dumps(observed))
