from pathlib import Path
import sys,json,re,html,os
from manuscript import TITLE,AUTHOR,AFFILIATIONS,EMAIL,ABSTRACT,PAGES
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT
REPO='https://github.com/stenichele/NCA-weight-space-reprogramming'
SITE='https://stenichele.github.io/NCA-weight-space-reprogramming/'

def web():
    players=json.loads((OUT/'data/players.json').read_text())
    def fig(name,caption):return f'<figure class="wide"><img src="assets/{name}" alt="{html.escape(caption)}" loading="lazy"><figcaption>{caption}</figcaption></figure>'
    def block(b):
        if b[0]=='p':return '<p>'+b[1]+'</p>'
        if b[0]=='h3':return '<h3>'+b[1]+'</h3>'
        if b[0]=='eq':return '<div class="equation">'+b[1]+'</div>'
        if b[0]=='fig':return fig(b[1],b[2])
        if b[0]=='table':return '<div class="table-wrap wide"><table><thead><tr>'+''.join('<th>'+v+'</th>' for v in b[1])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in b[2])+'</tbody></table></div>'
    def player(key):
        item=players[key];canv=''.join(f'<div class="animation-cell"><strong>{html.escape(name)}</strong><canvas width="260" height="260" aria-label="{html.escape(name)} simulated trajectory"></canvas></div>' for name in item['names'])
        note='Uniform sampling: one frame every 4 NCA steps.' if key!='persistence' else 'Checkpoint playback: unequal time gaps. Read the step counter; playback speed is not simulation speed.'
        return f'<div class="player wide" data-player="{key}"><div class="animation-grid" style="--cols:{len(item["names"])}">{canv}</div><div class="controls"><button type="button" class="play">Play from seed</button><input type="range" min="0" max="{len(item["times"])-1}" value="0" aria-label="Simulation checkpoint"><output>Step 0</output></div><p class="player-note">{note} These are recorded NCA states, not generated illustrations.</p></div>'
    sections=[]
    for p in PAGES:
        h=f'<section id="{p["id"]}">'
        if p.get('kicker'):h+=f'<div class="kicker">{p["kicker"]}</div>'
        h+='<h2>'+p['title']+'</h2>'
        for i,b in enumerate(p['blocks']):
            h+=block(b)
            if i==0 and p.get('player'):h+=player(p['player'])
        h+='</section>';sections.append(h)
    notes=''
    for label,name in [('Six-edit submitted rationale','six_edits_explanation.txt'),('Persistence: 36 hypotheses and observations','persistence_experiment_log.txt'),('Persistence: committed mechanism and explanation','persistence_explanation.txt')]:
        txt=(OUT/'records'/name).read_text();notes+=f'<details><summary>{label}</summary><p><a href="records/{name}" download>Download this record</a></p><pre>{html.escape(txt)}</pre></details>'
    downloads='<div class="download-grid"><a href="report.pdf">PDF report<span>Paginated scientific manuscript</span></a><a href="downloads/reproducibility.zip" download>Code + weights<span>Simulator, constructions, checkpoints and data</span></a><a href="records/persistence_experiment_log.txt" download>Experiment log<span>Recorded hypotheses and outcomes</span></a><a href="code/persistence.py" download>Persistence construction<span>Exact original-to-edited weight algebra</span></a></div>'
    title=f'<header><div class="eyebrow">Research report · 3 November 2026</div><h1>{TITLE}</h1><p class="deck">Editing a shared local rule to change color, orientation, developmental speed, and long-term behavior.</p><div class="byline"><b>{AUTHOR}</b><span>{AFFILIATIONS[0]}<br>{AFFILIATIONS[1]}</span><a href="mailto:{EMAIL}">{EMAIL}</a></div><div class="header-links"><a href="report.pdf">Download PDF</a><a href="downloads/reproducibility.zip" download>Code &amp; weights</a><a href="#research-notes">Astra’s research notes</a><a href="https://github.com/stenichele/NCA-weight-space-reprogramming">GitHub</a></div></header>'
    nav='<nav aria-label="Article sections"><b>In this report</b>'+''.join(f'<a href="#{p["id"]}">{p["title"]}</a>' for p in PAGES)+'</nav>'
    hero=fig('overview.png','Overview. Seven weight edits of the same growing gecko. Frames are taken at step 96, except the half-speed example at step 128. Every panel is a simulation of the corresponding checkpoint.')
    body=title+nav+'<main><div class="abstract"><span>Abstract</span><p>'+ABSTRACT+'</p></div>'+hero+'<div class="highlights wide"><div><strong>8,336</strong><span>shared NCA parameters</span></div><div><strong>7 edits</strong><span>one starting morphology</span></div><div><strong>8/8</strong><span>persistent through 8,192 steps</span></div></div>'+''.join(sections)+'<section id="research-notes"><h2>Astra’s research notes</h2><p>Inspect the recorded experimental hypotheses and submitted explanations below. These are the available research artifacts, not a complete private internal chain-of-thought.</p>'+notes+'</section><section id="downloads"><h2>Code, weights and data</h2>'+downloads+'<p>The <a href="https://github.com/stenichele/NCA-weight-space-reprogramming#readme">README</a> gives commands, numerical conventions and provenance. <a href="data/manifest.json">File hashes</a> identify the included checkpoints. Browse the <a href="https://github.com/stenichele/NCA-weight-space-reprogramming">GitHub repository</a>, including <a href="https://github.com/stenichele/NCA-weight-space-reprogramming/tree/main/code">code</a>, <a href="https://github.com/stenichele/NCA-weight-space-reprogramming/tree/main/weights">all checkpoints</a>, <a href="https://github.com/stenichele/NCA-weight-space-reprogramming/tree/main/data">evaluation data</a>, and <a href="https://github.com/stenichele/NCA-weight-space-reprogramming/tree/main/records">research notes</a>. Download the repository ZIP to use the report offline.</p></section></main><footer>'+AUTHOR+' · '+EMAIL+'<br>Report based on recorded experiments. No NCA training or gradient optimization was performed during editing.</footer>'
    css='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;color:#243b49;background:#fff;font:18px/1.73 Georgia,"Times New Roman",serif}header{max-width:1050px;margin:0 auto;padding:65px 30px 40px;border-bottom:1px solid #dbe2e3}h1{font:600 clamp(36px,4.4vw,61px)/1.08 system-ui,sans-serif;letter-spacing:-1.8px;max-width:1000px;margin:20px 0 24px}h2{font:600 31px/1.23 system-ui,sans-serif;letter-spacing:-.6px;margin:12px 0 23px}h3{font:650 20px/1.35 system-ui,sans-serif;margin-top:28px}.eyebrow,.kicker{font:600 12px/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:1.9px;color:#078188}.deck{font:22px/1.5 system-ui,sans-serif;max-width:820px;color:#61747b}.byline{display:grid;gap:9px;font:14px/1.65 system-ui,sans-serif;margin:26px 0}.byline b{font-size:17px;color:#1e3441}.header-links{display:flex;gap:25px;flex-wrap:wrap;font:600 14px system-ui,sans-serif;margin-top:28px}a{color:#087c83;text-decoration-thickness:1px;text-underline-offset:3px}main{max-width:750px;margin:0 auto;padding:40px 25px 70px}.abstract{font-size:18px;line-height:1.7}.abstract>span{font:700 12px system-ui,sans-serif;text-transform:uppercase;letter-spacing:1.6px}.wide{width:min(1050px,calc(100vw - 48px));position:relative;left:50%;transform:translateX(-50%)}figure{margin:32px 0 40px}figure img{display:block;width:100%;height:auto}figcaption{font:13px/1.6 system-ui,sans-serif;color:#60717a;margin:12px auto 0;max-width:900px}section{padding-top:54px;border-top:1px solid #dbe2e3;margin-top:46px}section p{margin:16px 0}code{font:14px ui-monospace,monospace;background:#edf3f4;padding:2px 5px;border-radius:3px}.equation{font:17px/1.7 ui-monospace,monospace;background:#f2f6f6;border-left:3px solid #16858b;padding:18px 22px;overflow:auto;margin:22px 0;white-space:pre-wrap}.table-wrap{margin:28px 0 34px;overflow:auto}table{border-collapse:collapse;width:100%;font:14px/1.5 system-ui,sans-serif}th{text-align:left;background:#eef4f4;color:#264552}th,td{padding:12px 14px;border-bottom:1px solid #dbe4e4;vertical-align:top}td:first-child{font-weight:600}nav{position:fixed;top:45px;left:max(12px,calc((100vw - 1430px)/2));width:185px;font:12px/1.5 system-ui,sans-serif;display:flex;flex-direction:column;gap:11px;color:#70828b}nav b{font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px}nav a{text-decoration:none;color:#71818a}nav a.active{color:#087c83;font-weight:700}.highlights{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #dbe4e4;border-bottom:1px solid #dbe4e4;margin:35px 0;padding:24px 0;text-align:center;font:14px system-ui,sans-serif}.highlights strong{display:block;color:#087f83;font-size:31px;margin-bottom:7px}.highlights span{color:#637580}.player{background:#f7faf9;border:1px solid #dbe4e4;border-radius:8px;margin:26px 0 34px;padding:18px}.animation-grid{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:12px}.animation-cell{background:#fff;text-align:center;padding:13px 8px 0}.animation-cell strong{font:600 13px system-ui,sans-serif;display:block;min-height:32px}.animation-cell canvas{width:100%;height:auto;image-rendering:pixelated}.controls{display:flex;gap:17px;align-items:center;margin:18px 3px 5px}.controls button{background:#087f83;color:white;border:0;border-radius:5px;padding:11px 15px;cursor:pointer;font:600 13px system-ui,sans-serif;min-width:125px}.controls input{flex:1;accent-color:#087f83;min-width:80px}.controls output{font:600 13px ui-monospace,monospace;min-width:90px}.player .player-note{font:12px/1.5 system-ui,sans-serif;color:#657781;margin:12px 3px 0}details{margin:16px 0;border:1px solid #dbe4e4;border-radius:5px;padding:15px 18px}summary{cursor:pointer;font:600 16px/1.4 system-ui,sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.65 ui-monospace,monospace;max-height:650px;overflow:auto;padding:16px;background:#f4f7f6}.download-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;font:600 16px system-ui,sans-serif}.download-grid a{border:1px solid #ccdedd;padding:20px;text-decoration:none;border-radius:6px}.download-grid span{display:block;font-size:12px;font-weight:400;line-height:1.5;margin-top:8px;color:#637780}footer{max-width:1050px;margin:auto;padding:28px 30px 45px;border-top:1px solid #dbe4e4;font:12px/1.7 system-ui,sans-serif;color:#71838c}@media(max-width:1450px){nav{display:none}}@media(max-width:700px){header{padding:35px 24px}h1{letter-spacing:-1px}.deck{font-size:19px}body{font-size:17px}main{padding:28px 24px}.wide{width:calc(100vw - 30px)}h2{font-size:27px}.animation-grid{grid-template-columns:repeat(2,1fr)}.controls{flex-wrap:wrap}.controls input{min-width:40%}.highlights strong{font-size:25px}.highlights span{font-size:11px}.download-grid{grid-template-columns:1fr}th,td{padding:9px;font-size:12px}.player{padding:10px}}@media print{nav,.player,.header-links,details{display:none}section{break-before:page}body{font-size:11pt}main,header{max-width:none}.wide{width:100%;left:auto;transform:none}}'''
    js='''const PLAYERS=__PLAYERS__;document.querySelectorAll('[data-player]').forEach(el=>{const config=PLAYERS[el.dataset.player],img=new Image(),canvases=[...el.querySelectorAll('canvas')],slider=el.querySelector('input'),out=el.querySelector('output'),button=el.querySelector('button');let index=config.times.indexOf(96),playing=false,started=false,last=0;slider.value=index;function draw(){canvases.forEach((c,i)=>{const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,c.width,c.height);ctx.drawImage(img,i*config.cell,index*config.cell,config.cell,config.cell,0,0,c.width,c.height)});slider.value=index;out.textContent='Step '+config.times[index].toLocaleString()}function tick(t){if(!playing)return;if(t-last>(el.dataset.player==='persistence'?800:80)){last=t;index++;if(index>=config.times.length){index=config.times.length-1;playing=false;button.textContent='Replay from seed'}draw()}if(playing)requestAnimationFrame(tick)}img.onload=draw;img.src=config.src;slider.addEventListener('input',()=>{playing=false;button.textContent='Play';index=Number(slider.value);started=true;draw()});button.addEventListener('click',()=>{if(playing){playing=false;button.textContent='Resume';return}if(!started||index===config.times.length-1){index=0;draw()}started=true;playing=true;button.textContent='Pause';last=performance.now();requestAnimationFrame(tick)})});const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))}})},{rootMargin:'-15% 0px -65% 0px'});document.querySelectorAll('main section[id]').forEach(s=>observer.observe(s));'''.replace('__PLAYERS__',json.dumps(players))
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="Stefano Nichele"><meta name="description" content="Seven weight-only edits of a local recurrent neural cellular automaton, with GPT-6 Astra, simulations, mechanisms and reproducible weights."><title>'+TITLE+'</title><style>'+css+'</style></head><body>'+body+'<script>'+js+'</script></body></html>')

def pdf():
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image as RLImage,Table,TableStyle,PageBreak,KeepTogether,KeepInFrame
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT,TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PIL import Image as PILImage
    if os.environ.get('REPORT_FONTS'):
        fonts=Path(os.environ['REPORT_FONTS'])
    else:
        import matplotlib
        fonts=Path(matplotlib.get_data_path())/'fonts/ttf'
    (ROOT/'work').mkdir(exist_ok=True)
    for name,file in [('Body','DejaVuSerif.ttf'),('Body-Bold','DejaVuSerif-Bold.ttf'),('Body-Italic','DejaVuSerif-Italic.ttf'),('Sans','DejaVuSans.ttf'),('Sans-Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-Bold');pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Sans-Bold',italic='Sans',boldItalic='Sans-Bold')
    ink=colors.HexColor('#243b49');teal=colors.HexColor('#087f83');gray=colors.HexColor('#647780');rule=colors.HexColor('#dbe4e4')
    st={
      'body':ParagraphStyle('body',fontName='Body',fontSize=9.6,leading=13.4,textColor=ink,spaceAfter=9),
      'title':ParagraphStyle('title',fontName='Sans-Bold',fontSize=29,leading=32,textColor=ink,spaceAfter=17),
      'h2':ParagraphStyle('h2',fontName='Sans-Bold',fontSize=19,leading=23,textColor=ink,spaceAfter=14),
      'h3':ParagraphStyle('h3',fontName='Sans-Bold',fontSize=11.5,leading=15,textColor=ink,spaceBefore=8,spaceAfter=7),
      'meta':ParagraphStyle('meta',fontName='Sans',fontSize=9.4,leading=14,textColor=gray,spaceAfter=7),
      'cap':ParagraphStyle('cap',fontName='Sans',fontSize=8.1,leading=11,textColor=gray,spaceBefore=5,spaceAfter=11),
      'eq':ParagraphStyle('eq',fontName='Sans',fontSize=10.2,leading=15,textColor=teal,backColor=colors.HexColor('#f0f6f5'),borderPadding=9,spaceBefore=5,spaceAfter=14),
      'cell':ParagraphStyle('cell',fontName='Sans',fontSize=8.4,leading=11.4,textColor=ink),
      'headcell':ParagraphStyle('headcell',fontName='Sans-Bold',fontSize=8.4,leading=11.4,textColor=ink),
      'abstract':ParagraphStyle('abstract',fontName='Body',fontSize=9.6,leading=13.4,textColor=ink,spaceAfter=13),
      'kicker':ParagraphStyle('kicker',fontName='Sans-Bold',fontSize=8,leading=11,textColor=teal,spaceAfter=8)}
    def clean(t):
        t=t.replace('–','-').replace('—',' - ').replace('‑','-')
        t=t.replace('<code>','<font name="Mono">').replace('</code>','</font>')
        return t
    def para(t,style='body'):return Paragraph(clean(t),st[style])
    width=507.3
    def image(name,cap,maxh=220):
        path=OUT/'assets'/name
        if name=='persistence_frames.png':
            path=ROOT/'work/persistence_pdf_frames.png';im=PILImage.open(OUT/'assets'/name);im.crop((0,0,im.width,506)).save(path)
            cap=cap.replace('The trained persistent checkpoint is a separate positive control. ','')+' The positive control is included in Figure 10.'
        im=PILImage.open(path);w=width;h=w*im.height/im.width
        if h>maxh:w*=maxh/h;h=maxh
        obj=RLImage(str(path),width=w,height=h);obj.hAlign='CENTER'
        return KeepInFrame(width,maxh+80,[obj,para(cap,'cap')],mode='shrink')
    def table(head,rows):
        n=len(head)
        if head[0]=='Condition':ww=[100,198,209.3]
        elif n==4:ww=[165,114,114,114.3]
        elif n==3:ww=[132,208,167.3]
        else:ww=[165,342.3]
        data=[[para(c,'headcell') for c in head]]+[[para(c,'cell') for c in r] for r in rows]
        t=Table(data,colWidths=ww,hAlign='LEFT',repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf4f4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.45,rule),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));return t
    class Paper(SimpleDocTemplate):
        def afterFlowable(self,flowable):
            if isinstance(flowable,Paragraph) and flowable.style.name=='h2':
                key='p'+str(self.page);self.canv.bookmarkPage(key);self.canv.addOutlineEntry(flowable.getPlainText(),key,0,False)
    def page(c,doc):
        c.setTitle(TITLE);c.setAuthor(AUTHOR);c.setSubject('Weight-only editing of local recurrent NCAs with GPT-6 Astra')
        if doc.page>1:
            key='section-'+str(doc.page);c.bookmarkPage(key);c.addOutlineEntry(PAGES[doc.page-2]['title'],key,0,False)
            c.setFillColor(gray);c.setFont('Sans',7.5);c.drawString(44,817,'WEIGHT SPACE REPROGRAMMING OF NEURAL CELLULAR AUTOMATA');c.drawRightString(551,817,'Stefano Nichele');c.setStrokeColor(rule);c.line(44,809,551,809)
        c.setStrokeColor(rule);c.line(44,35,551,35);c.setFillColor(gray);c.setFont('Sans',7.5);c.drawString(44,22,'3 November 2026  |  github.com/stenichele/NCA-weight-space-reprogramming');c.drawRightString(551,22,str(doc.page))
    doc=Paper(str(OUT/'report.pdf'),pagesize=(595.28,841.89),leftMargin=44,rightMargin=44,topMargin=48,bottomMargin=47,allowSplitting=1)
    story=[para('RESEARCH REPORT · 3 NOVEMBER 2026','kicker'),para(TITLE,'title'),para('<b>'+AUTHOR+'</b>','meta'),para(AFFILIATIONS[0]+'<br/>'+AFFILIATIONS[1]+'<br/><a href="mailto:'+EMAIL+'">'+EMAIL+'</a>','meta'),Spacer(1,7),para('ABSTRACT','kicker'),para(ABSTRACT,'abstract'),image('overview.png','Overview. Seven edits of one growing gecko; actual simulated states. Step 96, except half-speed at step 128. Synchronized animations are available in the web companion.',maxh=278)]
    for p in PAGES:
        story.append(PageBreak())
        page_start=len(story)
        if p.get('kicker'):story.append(para(p['kicker'],'kicker'))
        story.append(para(p['title'],'h2'))
        for b in p['blocks']:
            if b[0] in ['p','h3','eq']:story.append(para(b[1],{'p':'body','h3':'h3','eq':'eq'}[b[0]]))
            elif b[0]=='fig':
                mh=220 if b[1]=='speed_frames.png' else 220 if b[1]=='persistence_frames.png' else 210 if b[1]=='persistence_replicates.png' else 220
                story.append(image(b[1],b[2],mh))
            elif b[0]=='table':story.extend([table(b[1],b[2]),Spacer(1,12)])
        if p.get('player'):story.append(para('Animation: <a href="'+SITE+'#'+p['id']+'">open this experiment in the online report</a>.','cap'))
        page_content=story[page_start:];del story[page_start:];story.append(KeepInFrame(width,730,page_content,mode='shrink'))
    doc.build(story,onFirstPage=page,onLaterPages=page)

if __name__=='__main__':
    if len(sys.argv)==1 or sys.argv[1]=='web':web();print('Web report written.')
    elif sys.argv[1]=='pdf':pdf();print('PDF report written.')
