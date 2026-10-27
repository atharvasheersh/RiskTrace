"""Create a readable review PDF from the shared structured manuscript content.

This ReportLab PDF and the editable TeX share content; their pagination differs.
Renderer dependencies are deliberately separate from the frozen numerical lock.
"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font-dir',type=Path,default=ROOT/'.venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf')
    args=parser.parse_args()
    for name,file in [('Body','DejaVuSerif.ttf'),('Body-Bold','DejaVuSerif-Bold.ttf'),
                      ('Body-Italic','DejaVuSerif-Italic.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(args.font_dir/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-Bold')
    content=json.loads((ROOT/'paper/manuscript/content.json').read_text(encoding='utf8'))
    output=ROOT/'output/pdf/RiskTrace_Manuscript_Draft.pdf';output.parent.mkdir(parents=True,exist_ok=True)
    width,height=A4;usable=width-100
    styles={
        'title':ParagraphStyle('Title',fontName='Body-Bold',fontSize=18,leading=24,alignment=TA_CENTER,spaceAfter=16),
        'status':ParagraphStyle('Status',fontName='Body-Bold',fontSize=9,leading=13,textColor=colors.HexColor('#9b2424'),alignment=TA_CENTER,spaceAfter=12),
        'author':ParagraphStyle('Author',fontName='Body',fontSize=10,leading=14,alignment=TA_CENTER,spaceAfter=16),
        'h':ParagraphStyle('Heading',fontName='Body-Bold',fontSize=12,leading=16,spaceBefore=14,spaceAfter=7,keepWithNext=True),
        'body':ParagraphStyle('Body',fontName='Body',fontSize=10,leading=14,alignment=TA_JUSTIFY,spaceAfter=8),
        'small':ParagraphStyle('Small',fontName='Body',fontSize=8,leading=11,spaceAfter=5),
        'caption':ParagraphStyle('Caption',fontName='Body-Italic',fontSize=9,leading=12,spaceAfter=10),
        'cell':ParagraphStyle('Cell',fontName='Body',fontSize=7,leading=9),
        'header':ParagraphStyle('Header',fontName='Body-Bold',fontSize=7,leading=9,textColor=colors.white),
    }
    def p(s,style='body'):return Paragraph(html.escape(str(s)),styles[style])
    refs={r['key']:i for i,r in enumerate(content['references'],1)}
    story=[p(content['title'],'title'),p(content['status'],'status'),p(content['proposed_authors'],'author'),
           p('Abstract','h'),p(content['abstract'])]
    for section in content['sections']:
        story.append(p(section['title'],'h'))
        story.extend(p(text) for text in section['paragraphs'])
        if section['citations']:
            story.append(p('References: '+', '.join('['+str(refs[key])+']' for key in section['citations'])+'.','small'))
    story.extend([PageBreak(),p('Tables','h')])
    for index,table in enumerate(content['tables'],1):
        story.append(p(f"Table {index}. {table['caption']}",'caption'))
        rows=[[p(c,'header' if j==0 else 'cell') for c in row] for j,row in enumerate(table['rows'])]
        columns=len(rows[0]);weights=[1.35]+[1]*(columns-1)
        grid=Table(rows,colWidths=[usable*w/sum(weights) for w in weights],repeatRows=1,hAlign='LEFT')
        grid.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#243f58')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f1f4f6'),colors.white]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#6c7d89'))]))
        story.extend([grid,Spacer(1,20)])
    for index,figure in enumerate(content['figures'],1):
        story.extend([PageBreak(),p(f'Figure {index}','h')])
        path=ROOT/'paper/figures'/figure['file']
        with PILImage.open(path) as img:w,h=img.size
        scale=min(usable/w,580/h)
        story.extend([Image(str(path),width=w*scale,height=h*scale),Spacer(1,12),
                      p(f"Figure {index}. {figure['caption']}",'caption')])
    story.extend([PageBreak(),p('References','h')])
    for index,r in enumerate(content['references'],1):
        url=r.get('url',r.get('doi',''))
        parts=[f"[{index}] {r['author']} ({r['year']})",r['title'].rstrip('.'),r.get('journal',r.get('booktitle','')),url]
        text='. '.join(part for part in parts if part)
        story.append(p(text,'small'))
    def page(canvas,doc):
        canvas.saveState();canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor('#596873'))
        canvas.drawString(50,height-30,'RiskTrace | Exploratory working draft | 27 October 2026')
        canvas.line(50,height-37,width-50,height-37)
        canvas.drawString(50,28,'Author and finance review pending - no submission approval')
        canvas.drawRightString(width-50,28,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=53,bottomMargin=48,
        title=content['title'],author='Proposed contributors; author approval pending',pageCompression=1)
    doc.build(story,onFirstPage=page,onLaterPages=page)
    print(output)


if __name__=='__main__':main()
