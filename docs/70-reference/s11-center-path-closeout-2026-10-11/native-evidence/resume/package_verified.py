"""Package exact verified code, records and test logs; no media or new mutation."""
from pathlib import Path
import base64, hashlib, io, json, tarfile
OUT=Path(__file__).parent
ROOT=OUT.parents[2]
OLD=ROOT/'sample/output/s11-center-path-20261011-002'
items={
 'implementation.patch':OLD/'implementation.patch',
 'prior-execution-summary.json':OLD/'execution-summary.json',
 'implementation-evidence.md':ROOT/'docs/60-evidence/s11/2026-10-11-center-path-implementation.md',
 'resume-verification.json':OUT/'resume-verification.json',
 'resume-verify.py':OUT/'resume_verify.py',
 'before.json':OUT/'before.json',
 'replay-readout.json':OUT/'replay/readout.json',
 'replay-preflight.json':OUT/'replay/preflight.json',
 'pytest.xml':OUT/'pytest.xml',
}
for name in ('pytest','prepare','replay','governance','diff-check','patch-apply-check'):
 items[name+'.log']=OUT/(name+'.log')
data={name:p.read_bytes() for name,p in items.items()}
data['PAYLOAD-SHA256SUMS.txt']=''.join(f'{hashlib.sha256(b).hexdigest()}  {n}\n' for n,b in sorted(data.items())).encode()
archive=OUT/'verified-delivery.tar.xz'
with tarfile.open(archive,'w:xz') as tar:
 for name,b in sorted(data.items()):
  info=tarfile.TarInfo(name); info.size=len(b); info.mtime=0; tar.addfile(info,io.BytesIO(b))
encoded=base64.b64encode(archive.read_bytes()).decode()
(OUT/'verified-delivery.b64').write_text('\n'.join(encoded[i:i+100] for i in range(0,len(encoded),100))+'\n')
print(json.dumps({'bytes':archive.stat().st_size,'base64_chars':len(encoded),'lines':(len(encoded)+99)//100,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(data)},indent=2))
