"""Build an accurate narrated ARGUS submission demo from current project evidence."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from textwrap import fill
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "submission-assets"
AUDIO = HERE / "submission-audio"
OUTPUT = HERE / "ARGUS-Consumer-Submission-Demo.mp4"
W, H = 1920, 1080
BG, WHITE, INK, MUTED = "#F4F8FC", "#FFFFFF", "#142A45", "#637891"
LINE, BLUE, BLUE_SOFT = "#D9E4EF", "#087FBD", "#E9F5FB"
TEAL, TEAL_SOFT, AMBER, AMBER_SOFT = "#008B80", "#E8F6F2", "#C66A07", "#FFF5E5"
PURPLE, RED, GREEN, GREEN_SOFT = "#6246D4", "#C14D3D", "#168265", "#E9F8F1"

SCENES = [
    {"kind": "cover", "eyebrow": "ARGUS CONSUMER  /  TRACK C", "title": "Evidence before\nconclusions", "caption": "A public-data financial research prototype for consumer and retail companies.", "narration": "Meet ARGUS Consumer, a public-data financial research prototype. It searches public sources, traces approved values, and abstains when the evidence is not ready."},
    {"kind": "intake", "eyebrow": "01  /  ONLINE SOURCE INTAKE", "title": "Start with a company.\nFind a public report.", "caption": "Search public sources, select a report, cache it, and extract page-linked candidate claims.", "narration": "Search a company, choose a public report, and cache its SHA-256 fingerprint. ARGUS extracts review candidates; a recent Dabur report yielded six, none auto-approved."},
    {"kind": "review", "eyebrow": "02  /  HUMAN REVIEW GATE", "title": "A candidate is not\na verified fact.", "caption": "Review the source page, value, period, unit, statement basis, and reporting scope before approval.", "narration": "Review every claim against its page, unit, period, statement basis, and reporting scope. Ambiguous and missing values stay unresolved."},
    {"kind": "ledger", "eyebrow": "03  /  TRACEABLE EVIDENCE", "title": "Every approved value\nkeeps its provenance.", "caption": "HUL ledger examples: receivables and revenue, with the original filing page and source record.", "narration": "HUL ledger examples: about three thousand five hundred crore of FY2025 trade receivables on page 145, and revenue around sixty-one thousand five hundred crore on page 146. Each retains its source and review trail."},
    {"kind": "agents", "eyebrow": "04  /  DETERMINISTIC ANALYSIS", "title": "AI can help research.\nPython owns the numbers.", "caption": "The LLM adapter is qualitative and was not called in the saved HUL analysis.", "narration": "Python owns the financial calculations. An optional LLM adapter can produce qualitative hypotheses, never numbers. It was not called in this saved HUL run."},
    {"kind": "hul", "eyebrow": "05  /  CURRENT HUL DOSSIER", "title": "One unusual period\nis a reason to review.", "caption": "Standalone pre-demerger receivable days: FY2025 is above its calculated historical range.", "narration": "HUL has thirty verified observations across seven panels. Receivable days reached about twenty in FY2025, above the expected range of roughly eight to nineteen. Only one period was flagged."},
    {"kind": "abstention", "eyebrow": "06  /  RESULT: ABSTAIN", "title": "No reliable finding\ncleared the gates.", "caption": "Only one period is flagged; persistence, peer coverage, and independent evidence remain insufficient.", "narration": "ARGUS found no reliable finding. Persistence needs three consecutive periods; peer coverage is insufficient, volume is not comparable, and red-team explanations remain untested."},
    {"kind": "evaluation", "eyebrow": "07  /  MEASURED LIMITS", "title": "Synthetic checks pass.\nReal-world validation remains.", "caption": "Synthetic evaluation is labeled as synthetic; no real-company discovery or accuracy claim is made.", "narration": "On synthetic tests, recall was one hundred percent across twenty planted cases, false positives five percent across twenty clean cases, and missing-data abstention four of four. Real-world validation is unavailable."},
    {"kind": "close", "eyebrow": "ARGUS CONSUMER  /  PROTOTYPE STATUS", "title": "Trace the evidence.\nRespect the gaps.", "caption": "Online intake works. Broader comparable peer histories and real-world validation are next.", "narration": "ARGUS makes no investment recommendation. Online intake works; broader peer histories and real-world validation remain next. Trace the evidence. Respect the gaps."},
]

def font(size: int, weight: str = "regular"):
    path = Path(r"C:\Windows\Fonts") / ({"regular": "segoeui.ttf", "medium": "seguisb.ttf", "bold": "segoeuib.ttf"}[weight])
    return ImageFont.truetype(str(path), size)

def text(draw, xy, value, size=20, color=INK, weight="regular"):
    draw.text(xy, value, font=font(size, weight), fill=color)

def fit(draw, x, y, value, max_width, size=20, color=INK, weight="regular"):
    while size > 13 and draw.textbbox((0, 0), value, font=font(size, weight))[2] > max_width:
        size -= 1
    text(draw, (x, y), value, size, color, weight)

def card(draw, box, fill=WHITE, outline=LINE, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def pill(draw, x, y, label, fill, color, width=None, height=36, size=14):
    if width is None:
        width = draw.textbbox((0, 0), label, font=font(size, "medium"))[2] + 28
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill)
    text(draw, (x + 14, y + 7), label, size, color, "medium")
    return width

def base(scene, number):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # Persistent product header and page rhythm.
    d.rectangle((0, 0, W, 84), fill=WHITE)
    d.line((0, 83, W, 83), fill=LINE, width=2)
    d.rounded_rectangle((45, 19, 92, 66), radius=13, fill=BLUE)
    text(d, (59, 22), "A", 29, WHITE, "bold")
    text(d, (107, 25), "ARGUS", 27, INK, "bold")
    text(d, (243, 30), "Autonomous Consumer Financial Intelligence", 18, MUTED, "medium")
    pill(d, 1500, 22, "TRACK C  ·  FMCG & RETAIL", "#EFF4F9", "#40536D", 347, 38, 14)
    text(d, (62, 112), scene["eyebrow"], 16, TEAL, "bold")
    # Header title
    title_size = 43 if scene["kind"] in {"cover", "close"} else 38
    yy = 150
    for line in scene["title"].splitlines():
        text(d, (62, yy), line, title_size, INK, "bold")
        yy += title_size + 13
    # Burned-in narration subtitles. The companion SRT carries the same captions.
    d.rounded_rectangle((62, 912, 1858, 1007), radius=15, fill="#17314F")
    subtitle_font = font(25, "medium")
    words = scene["narration"].split()
    lines, line = [], ""
    for word in words:
        candidate = word if not line else line + " " + word
        if d.textbbox((0, 0), candidate, font=subtitle_font)[2] <= 1720:
            line = candidate
        else:
            lines.append(line); line = word
    if line: lines.append(line)
    line_h = 31
    sy = 912 + (95 - len(lines)*line_h)//2
    for subtitle_line in lines[:3]:
        text(d, (91, sy), subtitle_line, 25, WHITE, "medium")
        sy += line_h
    d.line((62, 1016, 1858, 1016), fill=LINE, width=2)
    text(d, (1775, 1030), f"{number:02d} / {len(SCENES):02d}", 16, MUTED, "bold")
    return im, d

def render(scene, index, out):
    im, d = base(scene, index)
    kind = scene["kind"]
    if kind == "cover":
        card(d, (62, 345, 1858, 934), "#EFF9FB", "#D7E7EF", 27, 2)
        pill(d, 111, 392, "PUBLIC SOURCES", WHITE, BLUE, 230, 44, 16)
        pill(d, 365, 392, "VERIFIED LEDGER", WHITE, TEAL, 250, 44, 16)
        pill(d, 638, 392, "DETERMINISTIC ANALYSIS", WHITE, PURPLE, 320, 44, 16)
        pill(d, 983, 392, "EVIDENCE-GROUNDED ABSTENTION", AMBER_SOFT, AMBER, 390, 44, 15)
        # Simple end-to-end route.
        nodes = [(160, "Search"), (550, "Review"), (940, "Calculate"), (1330, "Challenge"), (1710, "Report")]
        for i in range(len(nodes)-1):
            d.line((nodes[i][0] + 48, 670, nodes[i+1][0] - 48, 670), fill="#A8C3D3", width=6)
        for i, (cx, label) in enumerate(nodes):
            color = BLUE if i < 2 else TEAL if i < 4 else AMBER
            d.ellipse((cx - 42, 628, cx + 42, 712), fill=color, outline=WHITE, width=4)
            text(d, (cx - 20, 646), str(i+1), 28, WHITE, "bold")
            tw = d.textbbox((0,0), label, font=font(22,"medium"))[2]
            text(d, (cx - tw/2, 740), label, 22, INK, "medium")
        text(d, (111, 843), "A signal is useful only when its source, calculation, and limitations can be checked.", 22, MUTED, "medium")

    elif kind == "intake":
        # A product-style intake panel plus its review-safe result.
        card(d, (62, 322, 1120, 949), WHITE, LINE, 22)
        text(d, (98, 354), "LIVE COMPANY INTAKE", 16, MUTED, "bold")
        card(d, (98, 398, 1084, 470), "#FBFDFF", "#C9D8E6", 12, 1)
        text(d, (122, 418), "Dabur India Limited", 23, INK, "medium")
        text(d, (100, 506), "Selected public report", 16, MUTED, "medium")
        card(d, (98, 543, 1084, 643), "#F4FAFD", "#D8E7EF", 13, 1)
        text(d, (122, 558), "Dabur Annual Report 2025–26", 20, INK, "bold")
        fit(d, 122, 592, "Official report PDF · source selected by reviewer", 890, 15, MUTED)
        rows = [("01", "Search public sources", GREEN), ("02", "Cache report and record SHA-256", GREEN), ("03", "Extract page-linked candidate claims", BLUE)]
        yy = 682
        for num, label, col in rows:
            d.ellipse((104, yy, 134, yy+30), fill=col)
            text(d, (112, yy+3), num, 13, WHITE, "bold")
            text(d, (151, yy+3), label, 18, INK, "medium")
            yy += 62
        card(d, (1160, 322, 1858, 949), "#FFFCF6", "#F0DFBB", 22)
        text(d, (1200, 359), "REVIEW QUEUE", 16, AMBER, "bold")
        text(d, (1200, 405), "6", 58, AMBER, "bold")
        text(d, (1274, 423), "extracted candidates", 23, INK, "medium")
        text(d, (1200, 500), "Every candidate is still unverified.", 21, INK, "bold")
        text(d, (1200, 546), "A person checks the PDF before approving any value.", 17, MUTED)
        pill(d, 1200, 617, "NO AUTOMATIC APPROVAL", AMBER_SOFT, AMBER, 294, 38, 14)
        text(d, (1200, 697), "Online intake example: Dabur FY2025–26", 16, MUTED, "medium")
        text(d, (1200, 752), "Source selection  →  PDF cache  →  review queue", 15, BLUE, "medium")

    elif kind == "review":
        card(d, (62, 322, 1858, 949), WHITE, LINE, 22)
        fields = [
            ("VALUE", "Does the number match the table?"),
            ("PERIOD", "Which financial year or quarter?"),
            ("UNIT", "Rupees, crore, days, or percent?"),
            ("BASIS", "Standalone or consolidated?"),
            ("SCOPE", "Did reporting scope change?"),
            ("SOURCE", "Which PDF page and exact row?"),
        ]
        for i, (head, desc) in enumerate(fields):
            col, row = i % 2, i // 2
            x, y = 99 + col*848, 365 + row*156
            card(d, (x, y, x+786, y+125), "#FAFCFE", LINE, 14, 1)
            pill(d, x+22, y+20, head, BLUE_SOFT if i<3 else TEAL_SOFT, BLUE if i<3 else TEAL, 112, 30, 12)
            fit(d, x+156, y+22, desc, 586, 19, INK, "medium")
            text(d, (x+22, y+77), "Confirm against original public source", 15, MUTED)
        pill(d, 100, 870, "APPROVED", "#E9F8F1", GREEN, 155, 36, 13)
        text(d, (276, 877), "confirmed rows enter the append-only ledger", 17, GREEN, "medium")
        pill(d, 932, 870, "UNRESOLVED", AMBER_SOFT, AMBER, 168, 36, 13)
        text(d, (1118, 877), "missing or conflicting data stays missing", 17, AMBER, "medium")

    elif kind == "ledger":
        card(d, (62, 322, 1858, 949), WHITE, LINE, 22)
        pill(d, 100, 350, "HINDUSTAN UNILEVER LIMITED", BLUE_SOFT, BLUE, 330, 38, 14)
        pill(d, 450, 350, "FY2025 · STANDALONE", TEAL_SOFT, TEAL, 250, 38, 14)
        headers = [(108,"LEDGER ID"),(290,"OBSERVATION"),(740,"VALUE"),(940,"UNIT"),(1215,"PDF PAGE"),(1430,"STATUS")]
        d.rounded_rectangle((95, 421, 1825, 475), radius=10, fill="#F2F7FB")
        for x, label in headers: text(d, (x, 438), label, 13, MUTED, "bold")
        rows = [("L0030", "Trade receivables", "3,450", "INR crore", "145"), ("L0028", "Revenue", "61,469", "INR crore", "146")]
        for i, row in enumerate(rows):
            y = 475 + i*132
            if i == 0: d.rectangle((96,y,1824,y+130), fill="#F6FBFE")
            d.line((98,y+130,1822,y+130), fill=LINE, width=1)
            vals=[(108,row[0],BLUE,"bold"),(290,row[1],INK,"medium"),(740,row[2],INK,"bold"),(940,row[3],MUTED,"regular"),(1215,row[4],BLUE,"medium")]
            for x, val, col, w in vals: text(d, (x,y+27), val, 19, col, w)
            pill(d, 1430, y+20, "VERIFIED", "#E8F7F0", GREEN, 126, 34, 13)
            text(d, (290,y+74), "BSE filing · source URL, cached hash, and page reference retained", 14, MUTED)
        text(d, (105, 781), "Provenance chain", 17, INK, "bold")
        steps = [(108,"Source URL"),(477,"Cached PDF"),(846,"SHA-256"),(1215,"PDF page"),(1584,"Reviewer")]
        for i,(x,label) in enumerate(steps):
            pill(d,x,824,label,BLUE_SOFT if i<4 else TEAL_SOFT,BLUE if i<4 else TEAL,210,42,15)
            if i < len(steps)-1: text(d,(x+247,831),"→",24,MUTED,"medium")

    elif kind == "agents":
        card(d, (62, 322, 920, 949), WHITE, LINE, 22)
        pill(d, 103, 354, "OPTIONAL LLM ADAPTER", "#F2EDFF", PURPLE, 300, 38, 14)
        text(d, (103, 420), "Language model", 27, INK, "bold")
        text(d, (103, 470), "Qualitative hypotheses only", 18, MUTED)
        text(d, (103, 510), "No retrieved sources in this run", 18, MUTED)
        text(d, (103, 550), "Cannot author financial values", 18, MUTED)
        text(d, (103, 590), "Not called in the saved HUL analysis", 18, MUTED)
        pill(d, 103, 671, "OPTIONAL · NOT USED IN THIS RUN", "#F2EDFF", PURPLE, 330, 36, 13)
        card(d, (962, 322, 1858, 949), "#F5FBFA", "#CDE6E1", 22)
        pill(d, 1003, 354, "CORE ANALYSIS", TEAL_SOFT, TEAL, 220, 38, 14)
        text(d, (1003, 420), "Python engine", 27, INK, "bold")
        text(d, (1003, 470), "Builds compatible company panels", 18, MUTED)
        text(d, (1003, 510), "Computes ratios and residuals", 18, MUTED)
        text(d, (1003, 550), "Applies unchanged validation gates", 18, MUTED)
        text(d, (1003, 590), "Carries supporting ledger IDs", 18, MUTED)
        pill(d, 1003, 671, "DETERMINISTIC · EVIDENCE-BOUND", TEAL_SOFT, TEAL, 343, 36, 13)
        card(d, (103, 755, 1818, 879), WHITE, LINE, 15, 1)
        text(d, (135, 777), "This saved HUL analysis used the deterministic engine.", 21, INK, "bold")
        text(d, (135, 819), "No completed model red-team research is claimed for this run.", 17, MUTED)

    elif kind == "hul":
        # A real six-period receivable-days series, with latest tested range only.
        card(d, (62, 322, 1295, 949), WHITE, LINE, 22)
        text(d, (99, 350), "Receivable days · standalone pre-demerger cohort", 22, INK, "bold")
        text(d, (99, 386), "FY2020–FY2025 · six reported periods", 15, MUTED)
        pill(d, 946, 350, "FY2025 OUTSIDE RANGE", AMBER_SOFT, AMBER, 285, 36, 13)
        left, top, right, bottom = 155, 488, 1227, 804
        vals = [9.8707232,13.0776589,13.7749302,16.8787197,16.2817311,20.485936]
        names = ["FY20","FY21","FY22","FY23","FY24","FY25"]
        def y_at(v): return bottom-(v/24)*(bottom-top)
        def x_at(i): return left+i*(right-left)/5
        for tick in [0,5,10,15,20]:
            yy=y_at(tick); d.line((left,yy,right,yy),fill=LINE,width=2)
            text(d,(106,yy-13),str(tick),14,MUTED)
        x5=x_at(5); yhi=y_at(19.0617473); ylo=y_at(7.7908418)
        d.rounded_rectangle((x5-24,yhi,x5+24,ylo),radius=8,fill=BLUE_SOFT)
        d.line((x5-29,yhi,x5+29,yhi),fill=BLUE,width=3); d.line((x5-29,ylo,x5+29,ylo),fill=BLUE,width=3)
        points=[(x_at(i),y_at(v)) for i,v in enumerate(vals)]
        d.line(points,fill=NAVY if 'NAVY' in globals() else INK,width=5)
        for i,((xx,yy),val,name) in enumerate(zip(points,vals,names)):
            col=AMBER if i==5 else BLUE
            d.ellipse((xx-9,yy-9,xx+9,yy+9),fill=col,outline=WHITE,width=2)
            text(d,(xx-23,yy-35),f"{val:.1f}",14,col,"bold")
            text(d,(xx-23,bottom+20),name,14,MUTED,"medium")
        text(d,(100,876),"Latest expected range: 7.8–19.1 days. Earlier expected bounds are unavailable.",14,MUTED)
        card(d, (1320, 322, 1858, 949), "#FFFCF6", "#F0DFBB", 22)
        text(d,(1360,358),"CURRENT HUL RUN",15,AMBER,"bold")
        text(d,(1360,415),"30",52,BLUE,"bold"); text(d,(1450,433),"verified observations",16,MUTED)
        text(d,(1360,500),"7",52,PURPLE,"bold"); text(d,(1415,518),"audit panels",16,MUTED)
        d.line((1360,579,1818,579),fill="#E9DDBF",width=2)
        text(d,(1360,608),"Result",14,MUTED,"bold")
        fit(d,1360,639,"No Reliable Finding",430,26,AMBER,"bold")
        text(d,(1360,695),"One flagged receivables period",16,INK,"medium")
        text(d,(1360,735),"Persistence gate: 3 consecutive periods",14,MUTED)
        text(d,(1360,786),"0 candidates · 0 rejected",16,INK,"bold")

    elif kind == "abstention":
        card(d, (62, 322, 1858, 949), "#FFFCF5", "#F0DFBB", 22)
        text(d,(104,356),"DETERMINISTIC SCREENING VERDICT",16,AMBER,"bold")
        text(d,(104,393),"No persistent, peer-adjusted anomaly cleared the gates.",29,INK,"bold")
        reasons=[
            ("Persistence", "1 flagged period", "3 consecutive required", AMBER),
            ("Peer coverage", "Below the peer gate", "No reliable peer adjustment", AMBER),
            ("Volume history", "No comparable series", "Price-volume angle abstains", MUTED),
            ("Red-team", "Not tested", "No independent evidence retrieved", MUTED),
        ]
        for i,(head,val,note,col) in enumerate(reasons):
            x=104+(i%2)*850; y=500+(i//2)*184
            card(d,(x,y,x+790,y+145),WHITE,LINE,15,1)
            d.ellipse((x+22,y+27,x+38,y+43),fill=col)
            text(d,(x+56,y+18),head,17,INK,"bold")
            text(d,(x+56,y+53),val,20,col,"bold")
            text(d,(x+56,y+91),note,15,MUTED)
        pill(d, 104, 876, "0 FINDING CANDIDATES", WHITE, AMBER, 260, 38, 14)
        pill(d, 386, 876, "0 REJECTED FINDINGS", WHITE, MUTED, 250, 38, 14)
        text(d, (676, 884), "No real discovery is asserted.", 17, INK, "medium")

    elif kind == "evaluation":
        metrics=[("CANARY RECALL","100%","20 / 20 planted cases",BLUE),
                 ("FALSE POSITIVE RATE","5%","1 / 20 clean cases",AMBER),
                 ("MISSING-DATA ABSTAIN","100%","4 / 4 synthetic cases",TEAL),
                 ("DETERMINISM","100%","cache reruns",PURPLE)]
        for i,(head,value,detail,col) in enumerate(metrics):
            x=62+i*454
            card(d,(x,342,x+420,546),WHITE,LINE,18)
            text(d,(x+24,367),head,14,MUTED,"bold")
            text(d,(x+24,407),value,38,col,"bold")
            text(d,(x+24,466),detail,16,MUTED)
        card(d,(62,582,1858,949),"#FFFCF5","#F0DFBB",20)
        pill(d,100,614,"SYNTHETIC TESTS",AMBER_SOFT,AMBER,225,36,14)
        text(d,(100,678),"These results measure engineered test cases, not real-world accuracy.",23,INK,"bold")
        text(d,(100,728),"Real-company reconciliation: unavailable · published figures compared: 0",18,MUTED)
        text(d,(100,772),"Blind human baseline: unavailable · independent red-team evidence: not yet tested",18,MUTED)
        pill(d,100,842,"33 TESTS PASSED",GREEN_SOFT,GREEN,220,36,14)
        pill(d,343,842,"NO THRESHOLD CHANGES",BLUE_SOFT,BLUE,274,36,14)

    elif kind == "close":
        card(d,(62,350,1858,949),"#EFF9FB","#D7E7EF",27,2)
        columns=[(110,"WORKING NOW",["Online public-source search","PDF cache and extraction","Human verification workflow","Deterministic HUL screening"],BLUE),
                 (704,"EVIDENCE RULES",["Numbers stay ledger-grounded","Missing data stays unresolved","No discovery without validation","Abstention is a valid outcome"],TEAL),
                 (1298,"NEXT MILESTONES",["Broader comparable peer panels","Scope-matched volume history","Independent red-team evidence","Real-world validation"],AMBER)]
        for x,head,items,col in columns:
            card(d,(x,400,x+500,818),WHITE,LINE,18,1)
            pill(d,x+24,426,head,BLUE_SOFT if col==BLUE else TEAL_SOFT if col==TEAL else AMBER_SOFT,col,220,34,13)
            yy=488
            for item in items:
                d.ellipse((x+28,yy+6,x+40,yy+18),fill=col)
                fit(d,x+58,yy,item,410,17,INK,"medium")
                yy+=72
        text(d,(112,868),"ARGUS Consumer · Prototype demonstration · No investment recommendation",19,MUTED,"medium")

    im.save(out, optimize=True)

def audio_seconds(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
                            check=True, capture_output=True, text=True)
    return float(result.stdout.strip())

def srt_timestamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def build():
    ASSETS.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    rendered=[]
    for i, scene in enumerate(SCENES,1):
        frame=ASSETS/f"scene-{i:02d}.png"
        render(scene,i,frame)
        narration=AUDIO/f"scene-{i:02d}.mp3"
        if not narration.exists():
            raise FileNotFoundError(f"Missing narration audio: {narration}; run create_submission_audio.ps1")
        rendered.append((frame,narration,audio_seconds(narration)))
    # Merge edge-tts word-timed subtitle files into one sidecar matching the final video timeline.
    cues=[]
    offset=0.0
    cue_number=1
    for i, (_, narration, duration) in enumerate(rendered,1):
        subtitle_file=AUDIO/f"scene-{i:02d}.srt"
        if not subtitle_file.exists():
            raise FileNotFoundError(f"Missing subtitle file: {subtitle_file}")
        blocks=subtitle_file.read_text(encoding="utf-8-sig").strip().split("\n\n")
        for block in blocks:
            lines=block.splitlines()
            timing=next((line for line in lines if " --> " in line),None)
            if not timing: continue
            a,b=[part.strip() for part in timing.split(" --> ",1)]
            def parse_ts(value):
                hh,mm,rest=value.split(":"); ss,mmm=rest.split(",")
                return int(hh)*3600+int(mm)*60+int(ss)+int(mmm)/1000
            start, end=parse_ts(a)+offset, parse_ts(b)+offset
            cue_text="\n".join(lines[lines.index(timing)+1:]).strip()
            if cue_text:
                cues.append(f"{cue_number}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{cue_text}")
                cue_number+=1
        offset += duration + 0.32
    srt_path=HERE/"ARGUS-Consumer-Submission-Demo.srt"
    srt_path.write_text("\n\n".join(cues)+"\n",encoding="utf-8")
    clips=[]
    for i,(frame,narration,duration) in enumerate(rendered,1):
        clip=ASSETS/f"clip-{i:02d}.mp4"
        total=duration+0.32
        fade=max(duration-0.25,0.1)
        vf=(f"fps=30,fade=t=in:st=0:d=0.28,fade=t=out:st={fade:.3f}:d=0.22,format=yuv420p")
        vf=f"scale=1280:720:flags=fast_bilinear,fps=24,fade=t=in:st=0:d=0.28,fade=t=out:st={fade:.3f}:d=0.22,format=yuv420p"
        cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-framerate","24","-i",str(frame),"-i",str(narration),
             "-vf",vf,"-af","apad=pad_dur=0.32","-t",f"{total:.3f}","-c:v","libx264","-preset","ultrafast","-crf","22",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-movflags","+faststart",str(clip)]
        subprocess.run(cmd,check=True)
        clips.append(clip)
    concat=ASSETS/"concat.txt"
    concat.write_text("".join(f"file '{clip.resolve().as_posix()}'\n" for clip in clips),encoding="utf-8")
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),
                    "-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
                    "-movflags","+faststart",str(OUTPUT)],check=True)
    manifest={"video":OUTPUT.relative_to(ROOT).as_posix(),"subtitles":srt_path.relative_to(ROOT).as_posix(),"voice":"Google TTS English (India; synthetic voice)",
              "scenes":len(SCENES),"narration_seconds":round(sum(x[2] for x in rendered),2),"bytes":OUTPUT.stat().st_size}
    (HERE/"submission-video-manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    build()
