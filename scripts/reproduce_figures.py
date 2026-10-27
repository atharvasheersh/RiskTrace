"""Rebuild the four scientific figures and check deterministic image outputs."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'paper/figures').glob('*') if p.suffix in ['.png','.svg']}


if __name__=='__main__':
    before=hashes()
    subprocess.run([sys.executable,str(ROOT/'scripts/build_figures.py')],cwd=ROOT,check=True)
    after=hashes();assert before==after,'Generated figure differs; inspect before replacing results'
    report=dict(status='passed',python=sys.version,prefix=sys.prefix,
        separate_environment=Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve(),
        figure_pairs=4,verified_byte_identical_outputs=after,
        scope='Rebuild figures and exact case extracts from saved frozen predictions/audits; not independent model training')
    (ROOT/'results/reproduction/figures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Rebuilt four PNG/SVG pairs; all eight outputs byte-identical')
