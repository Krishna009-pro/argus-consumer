"""Render a narrated ARGUS prototype walkthrough from verified current behavior."""
from __future__ import annotations

import argparse
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
W, H = 1600, 900
BG = (10, 20, 34)
PANEL = (18, 36, 55)
TEAL = (64, 213, 190)
TEXT = (241, 246, 250)
MUTED = (165, 183, 199)
AMBER = (255, 195, 91)

SCENES = [
    {
        "eyebrow": "ARGUS-CONSUMER  /  PROTOTYPE WALKTHROUGH",
        "title": "Financial research\nwith an evidence trail",
        "body": "Track C  ·  Consumer, FMCG & Retail\nPublic sources  ·  Deterministic metrics  ·  Explicit abstention",
        "tag": "CURRENT PROTOTYPE",
        "voice": "ARGUS Consumer is a public-data research prototype for consumer and retail financial signals.",
        "kind": "cover",
    },
    {
        "eyebrow": "TARGET LIVE WORKFLOW",
        "title": "Start from a company name",
        "body": "Find public sources  →  Build a timeline  →  Test financial angles\nCross-check claims  →  Challenge explanations  →  Report evidence",
        "tag": "LIVE SOURCE DISCOVERY IS NOT IMPLEMENTED YET",
        "voice": "Target: company name, public sources, comparable history, challenge, evidence report. Live source discovery remains.",
        "kind": "flow",
    },
    {
        "eyebrow": "WORKING NOW  /  LOCAL PUBLIC-SOURCE IMPORT",
        "title": "Import the report; keep its provenance",
        "body": "python scripts/argus.py import-local .\\data\\incoming\\report.pdf\n  --company \"Company Name\" --source-url https://official.example/report.pdf",
        "tag": "CONTENT HASH  ·  SOURCE URL  ·  PAGE SNIPPETS  ·  UNVERIFIED CANDIDATES",
        "voice": "Import an annual report locally. ARGUS caches and hashes it, then proposes page-linked figures.",
        "kind": "terminal",
    },
    {
        "eyebrow": "HUMAN REVIEW GATE",
        "title": "Candidates are not facts",
        "body": "Check each candidate against the original page:\nfigure  ·  unit  ·  period  ·  statement basis  ·  table context\n\nOnly reviewed observations can enter the evidence ledger.",
        "tag": "UNCERTAIN, MISSING OR CONFLICTING VALUES STAY UNRESOLVED",
        "voice": "Reviewers check values, units, periods, statement basis and scope. Uncertain rows stay unresolved.",
        "kind": "review",
    },
    {
        "eyebrow": "DETERMINISTIC ANALYSIS",
        "title": "Verified panels feed the engine",
        "body": "Comparable periods and units  →  Financial angle series\nPersistence  →  Peer adjustment  →  Evidence gates\n\nEvery calculated value carries its supporting ledger IDs.",
        "tag": "NO THRESHOLD CHANGES  ·  INSUFFICIENT EVIDENCE MEANS ABSTAIN",
        "voice": "Verified observations feed deterministic calculations. Persistence and evidence gates stay unchanged.",
        "kind": "engine",
    },
    {
        "eyebrow": "ACTUAL RUN  /  HINDUSTAN UNILEVER LIMITED",
        "title": "A verified HUL source batch",
        "body": "Standalone revenue  FY25 ₹59,676 cr  →  FY26 ₹61,975 cr\nConsolidated revenue  FY25 ₹61,328 cr  →  FY26 ₹64,468 cr\nContinuing operations · PDF pages 139 and 184\n12 verified observations · 6 compatible panels",
        "tag": "OFFICIAL REPORT  ·  HASHED SOURCE  ·  PAGE-LEVEL EVIDENCE",
        "voice": "For HUL, twelve figures were visually checked on PDF pages 138, 139, 183 and 184. Continuing revenue: standalone 61,975 crore in fiscal 2026 and 59,676 in fiscal 2025; consolidated 64,468 and 61,328. Page and file hash are retained.",
        "kind": "terminal",
    },
    {
        "eyebrow": "ACTUAL DETERMINISTIC RESULT",
        "title": "ARGUS abstains on this batch",
        "body": "2 comparable revenue periods; the gate requires 6\nNo verified volume history or eligible peer set\nBalance-sheet years split across demerger cohorts\n0 finding candidates generated · 0 rejected findings",
        "tag": "ABSTENTION  ·  NOT A REAL DISCOVERY",
        "voice": "ARGUS abstains: two revenue years versus the six-period gate; volume and eligible peers are missing. Balance sheets split around the demerger. No finding was generated. Six of 56 extracted note-number errors were rejected; fifty remain unverified.",
        "kind": "abstain",
    },
    {
        "eyebrow": "STATUS & NEXT MILESTONE",
        "title": "A working foundation; more to build",
        "body": "24 tests pass  ·  Dashboard health check: ok\nNo detection thresholds changed\n\nNext: add live public-source discovery and build\ncomparable multi-year history across companies.",
        "tag": "PROTOTYPE STATUS  ·  NOT YET AN AUTONOMOUS LIVE RESEARCH DEMO",
        "voice": "Twenty-four tests pass, dashboard health is okay, and thresholds are unchanged. This is a prototype, not a live discovery system. Longer comparable histories remain to be built.",
        "kind": "next",
    },
]


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = word if not line else line + " " + word
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def render_scene(scene: dict, index: int, path: Path) -> None:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # Subtle background grid and framing.
    for x in range(60, W, 100):
        d.line((x, 0, x, H), fill=(14, 29, 45), width=1)
    d.rounded_rectangle((70, 54, 1530, 846), radius=28, fill=BG, outline=(35, 63, 81), width=2)
    d.rounded_rectangle((70, 54, 1530, 120), radius=25, fill=PANEL)
    d.rectangle((70, 90, 1530, 120), fill=PANEL)
    d.ellipse((100, 79, 118, 97), fill=(250, 98, 105))
    d.ellipse((132, 79, 150, 97), fill=AMBER)
    d.ellipse((164, 79, 182, 97), fill=TEAL)
    d.text((215, 76), scene["eyebrow"], font=font(21, True), fill=MUTED)

    d.rounded_rectangle((118, 164, 1482, 770), radius=22, fill=PANEL)
    d.rounded_rectangle((118, 164, 128, 770), radius=5, fill=TEAL)
    title_f = font(54 if scene["kind"] != "cover" else 61, True)
    title_lines = scene["title"].splitlines()
    y = 219
    for line in title_lines:
        d.text((174, y), line, font=title_f, fill=TEXT)
        y += 72
    y += 24
    body_f = font(29 if scene["kind"] in {"flow", "review", "engine", "next"} else 25)
    if scene["kind"] == "terminal":
        d.rounded_rectangle((172, y-10, 1425, y+230), radius=16, fill=(7, 15, 25), outline=(42, 72, 90), width=2)
        y += 24
        for line in scene["body"].splitlines():
            d.text((205, y), line, font=font(25, line.startswith("status") or line.startswith("verified") or line.startswith("compatible") or line.startswith("rejected")), fill=TEAL if line.startswith("status") else TEXT)
            y += 49
    elif scene["kind"] == "flow":
        stages = ["PUBLIC SOURCES", "TIMELINE", "CALCULATE", "CHALLENGE", "EVIDENCE"]
        sx, sy, gap = 175, y+12, 235
        for i, stage in enumerate(stages):
            x = sx + i*gap
            d.rounded_rectangle((x, sy, x+205, sy+94), radius=14, fill=(24, 53, 69), outline=(51, 104, 116), width=2)
            d.text((x+17, sy+31), stage, font=font(18, True), fill=TEAL)
            if i < len(stages)-1:
                d.text((x+208, sy+26), "›", font=font(34, True), fill=MUTED)
        d.text((174, sy+133), "TARGET WORKFLOW — source retrieval is not yet implemented in this build.", font=font(22), fill=MUTED)
    else:
        lines = wrap(d, scene["body"], body_f, 1190)
        for line in lines:
            if line:
                d.text((174, y), line, font=body_f, fill=TEXT)
            y += 45

    tag_y = 704
    d.rounded_rectangle((168, tag_y, 1430, tag_y+44), radius=12, fill=(27, 52, 66))
    d.text((188, tag_y+10), scene["tag"], font=font(17, True), fill=AMBER if scene["kind"] in {"abstain", "next"} else TEAL)
    d.text((1340, 795), f"{index:02d} / {len(SCENES):02d}", font=font(17, True), fill=MUTED)
    im.save(path, optimize=True)


def audio_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def build(narration: Path, output: Path) -> None:
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for i, scene in enumerate(SCENES, 1):
        render_scene(scene, i, assets / f"scene-{i:02d}.png")
    duration = audio_duration(narration)
    weights = [max(len(s["voice"].split()) + s["voice"].count(",")*2 + s["voice"].count(".")*3, 1) for s in SCENES]
    total_weight = sum(weights)
    concat_file = OUT / "slides.ffconcat"
    with concat_file.open("w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for i, weight in enumerate(weights, 1):
            img = (assets / f"scene-{i:02d}.png").resolve().as_posix()
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration * weight / total_weight + 0.35:.3f}\n")
        f.write(f"file '{(assets / f'scene-{len(SCENES):02d}.png').resolve().as_posix()}'\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_file),
           "-i", str(narration), "-vsync", "vfr", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "medium",
           "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", str(output)]
    subprocess.run(cmd, check=True)
    print(f"Created {output} ({duration:.1f}s narration; {output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--narration", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT / "ARGUS-Consumer-Prototype-Demo.mp4")
    args = parser.parse_args()
    build(args.narration.resolve(), args.output.resolve())
