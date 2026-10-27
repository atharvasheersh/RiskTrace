"""Structural/text checks supplement the separately completed visual page review."""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__=='__main__':
    pdf=ROOT/'output/pdf/RiskTrace_Manuscript_Draft.pdf'
    docx=ROOT/'output/documents/RiskTrace_Revised_Work_Allocation_Ayush_Atharva.docx'
    qa=ROOT/'tmp/pdfs/allocation/RiskTrace_Revised_Work_Allocation_Ayush_Atharva.pdf'
    reader=PdfReader(pdf);assert len(reader.pages)==13
    text='\n'.join(p.extract_text() for p in reader.pages)
    for value in ['0.015143','13.49','12,783','0.006225','332','References','NOT APPROVED FOR SUBMISSION']:
        assert value in text,value
    assert '\ufffd' not in text
    document=Document(docx)
    text_doc='\n'.join(p.text for p in document.paragraphs)
    for value in ['TreeSHAP','Reproduce logistic regression and XGBoost independently','807','Atharva tasks']:
        assert value in text_doc,value
    assert all(not list(root.iter(qn('w:pBdr'))) for root in [document.element,document.styles.element])
    assert len(PdfReader(qa).pages)==5
    report=dict(status='passed',review_pdf_pages=13,allocation_docx_pages_in_Word_export=5,
        review_pdf_sha256=sha(pdf),allocation_docx_sha256=sha(docx),tex_source_sha256=sha(ROOT/'paper/manuscript/main.tex'),
        review_pdf_engine='ReportLab, from shared manuscript content.json',tex_compile='desktop compiler reported success on current source',
        docx_render='Packaged renderer missing LibreOffice; Microsoft Word export and Poppler rasterization used',
        visual_review='All13 manuscript pages and all5 actual DOCX-export pages inspected; affected pages rechecked after edits',
        boundaries='This checks document structure/text and records actual visual QA; not finance or author approval')
    (ROOT/'results/reproduction/document_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    development=[r for p in (ROOT/'results/predictive').glob('*_run_manifest.json') for r in json.loads(p.read_text())]
    final=json.loads((ROOT/'results/final_evaluation/fit_manifest.json').read_text())
    runs=json.loads((ROOT/'results/explanations/run_manifest.json').read_text())['runs']
    cost=dict(development_fits=len(development),final_fits=len(final),
        recorded_development_fit_seconds=sum(r['seconds'] for r in development),recorded_final_fit_seconds=sum(r['seconds'] for r in final),
        recorded_financial_audit_seconds=sum(r.get('seconds',0) for r in runs),
        cpu_threads_per_fit=2,logical_processors=12,physical_memory_bytes=16794324992,paid_compute=False,
        interpretation='Sum of recorded components, not total session wall time; setup, edge masks and document/review time not all included')
    (ROOT/'results/reproduction/execution_costs.json').write_text(json.dumps(cost,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Passed document structure/text checks; actual page review recorded; execution costs summarized')
