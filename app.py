"""Remove the vocals from a song: YouTube URL or audio file in, instrumental out. Runs locally.

    .venv/bin/python app.py        # opens http://127.0.0.1:7860
"""
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import gradio as gr
import torch
import yt_dlp

MODEL = "htdemucs_ft"  # Demucs' best vocals model; use "htdemucs" for ~4x faster, slightly dirtier results
# MPS needs macOS 15+: on macOS 14 it rejects conv outputs longer than 65536 samples, which htdemucs always produces.
MAC_15 = platform.system() == "Darwin" and int(platform.mac_ver()[0].split(".")[0]) >= 15
DEVICE = "mps" if MAC_15 and torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
OUT = Path(__file__).parent / "output"


def download(url: str, folder: Path) -> Path:
    opts = {"format": "bestaudio/best", "outtmpl": str(folder / "%(title)s.%(ext)s"), "noplaylist": True, "quiet": True,
            "js_runtimes": {"node": {}, "deno": {}},  # YouTube needs a JS runtime to solve its player challenges
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return Path(ydl.prepare_filename(ydl.extract_info(url))).with_suffix(".wav")


def instrumental(url: str, file: str | None) -> str:
    if not (url or "").strip() and not file:
        raise gr.Error("Paste a YouTube URL or upload an audio file.")
    with tempfile.TemporaryDirectory() as tmp:
        song = download(url.strip(), Path(tmp)) if (url or "").strip() else Path(file)
        subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", MODEL, "-d", DEVICE, "--mp3",
                        "-o", str(OUT), str(song)], check=True)
    return str(OUT / MODEL / song.stem / "no_vocals.mp3")


demo = gr.Interface(
    instrumental,
    [gr.Textbox(label="YouTube URL"), gr.Audio(type="filepath", label="…or upload an audio file")],
    gr.Audio(label="Instrumental"),
    title="Instrumental",
    description=f"Removes the vocals with Demucs ({MODEL}, on {DEVICE}). A 4-minute song takes a few minutes on a GPU/MPS, 10+ on CPU.",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
