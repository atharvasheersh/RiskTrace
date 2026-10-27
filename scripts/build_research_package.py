"""Build a local-only archive with Git history and exact preserved public data."""
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
        raise ValueError('Commit reviewed source/artifacts before building the bundle')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    folder=ROOT/'output/research_package';folder.mkdir(parents=True,exist_ok=True)
    bundle=folder/'RiskTrace_history.bundle'
    subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True)
    subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,check=True,capture_output=True)
    paths={};source_records=0
    for manifest in (ROOT/'data/manifests').glob('*sources.json'):
        entries=json.loads(manifest.read_text())
        if not isinstance(entries,list):continue
        for entry in entries:
            rel=entry.get('path','')
            if not rel.startswith('data/raw/'):continue
            path=(ROOT/rel).resolve();assert path.is_relative_to(ROOT/'data/raw')
            assert path.is_file() and digest(path)==entry['sha256'],rel
            paths[rel]=path;source_records+=1
            meta=path.with_suffix('.meta.json')
            if meta.exists():paths[meta.relative_to(ROOT).as_posix()]=meta
    for path in (ROOT/'data/processed').rglob('*'):
        if path.is_file() and path.suffix in ['.csv','.json']:paths[path.relative_to(ROOT).as_posix()]=path
    files=[dict(path=rel,bytes=path.stat().st_size,sha256=digest(path)) for rel,path in sorted(paths.items())]
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),code_commit=commit,
        dataset_id=json.loads((ROOT/'data/manifests/analysis_v1.json').read_text())['dataset_id'],
        bundle_sha256=digest(bundle),source_manifest_records_verified=source_records,
        snapshot_files=len(files),uncompressed_snapshot_bytes=sum(f['bytes'] for f in files),files=files,
        status='Local reproducibility archive; not uploaded or author-approved for public redistribution',
        exclusions=['environments','credentials','Git configuration','dependency and graph caches','third-party literature PDFs'],
        scope='Git bundle plus exact snapshots; inference/tables/figures reproduced; full training not rerun')
    readme=('RiskTrace local research package\n\nCode commit: '+commit+'\n\n'
        'Unzip and run: git clone RiskTrace_history.bundle RiskTrace\n'
        'Then in PowerShell run:\n'
        'Copy-Item -LiteralPath preserved_data\\data -Destination RiskTrace -Recurse -Force\n'
        'Set-Location RiskTrace\nuv sync --locked --extra dev\n\n'
        'Follow docs/reproduction_and_package.md. Git history is needed for original freeze checks.\n'
        'Verify snapshot_manifest.json and the external archive SHA before use.\n'
        'No submission, author approval, license choice or external publication is implied.\n')
    archive=folder/'RiskTrace_Research_Package.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.write(bundle,'RiskTrace_history.bundle');z.writestr('README.txt',readme)
        z.writestr('snapshot_manifest.json',json.dumps(manifest,indent=2)+'\n')
        for rel,path in sorted(paths.items()):z.write(path,'preserved_data/'+rel)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for f in files:assert hashlib.sha256(z.read('preserved_data/'+f['path'])).hexdigest()==f['sha256']
        assert hashlib.sha256(z.read('RiskTrace_history.bundle')).hexdigest()==manifest['bundle_sha256']
    report={k:v for k,v in manifest.items() if k!='files'}
    report.update(archive_path=archive.relative_to(ROOT).as_posix(),archive_sha256=digest(archive),
                  archive_bytes=archive.stat().st_size,validation='ZIP CRC, every snapshot SHA256 and bundle SHA256 passed')
    (ROOT/'results/reproduction/package_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
