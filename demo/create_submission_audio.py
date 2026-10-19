"""Generate natural-sounding synthetic narration and timed captions for the demo."""
from __future__ import annotations

import subprocess
from pathlib import Path

from gtts import gTTS

from create_submission_video import AUDIO, SCENES, audio_seconds, srt_timestamp

VOICE = "Google TTS English (India)"


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    for i, scene in enumerate(SCENES, 1):
        stem = AUDIO / f"scene-{i:02d}"
        mp3 = stem.with_suffix(".mp3")
        source_mp3 = Path(f"{stem}.source.mp3")
        print(f"Generating scene {i:02d}/{len(SCENES)} with {VOICE}...")
        gTTS(scene["narration"], lang="en", tld="co.in", slow=False).save(str(source_mp3))
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(source_mp3), "-filter:a", "atempo=1.12",
            "-c:a", "libmp3lame", "-q:a", "3", str(mp3),
        ], check=True)
        source_mp3.unlink()
        duration = audio_seconds(mp3)
        subtitle = f"1\n{srt_timestamp(0)} --> {srt_timestamp(duration)}\n{scene['narration']}\n"
        stem.with_suffix(".srt").write_text(subtitle, encoding="utf-8")


if __name__ == "__main__":
    main()
