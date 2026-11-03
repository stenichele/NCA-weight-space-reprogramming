"""Refresh file hashes and build the compact reproducibility archive."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'data/manifest.json'
data=json.loads(manifest.read_text())
folders=['code','weights','records','data','report_source']
files=sorted(p for f in folders for p in (ROOT/f).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=manifest)
files += [ROOT/n for n in ['README.md','REPRODUCIBILITY.txt','LICENSE','NOTICE.md','CITATION.cff']]
data['repository']='https://github.com/stenichele/NCA-weight-space-reprogramming'
data['web_report']='https://stenichele.github.io/NCA-weight-space-reprogramming/'
data['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest.write_text(json.dumps(data,indent=2)+'\n')
(ROOT/'downloads').mkdir(exist_ok=True)
with zipfile.ZipFile(ROOT/'downloads/reproducibility.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[manifest]:z.write(p,p.relative_to(ROOT))
print('Refreshed manifest and downloads/reproducibility.zip. For figures and animations, download the complete repository.')
