# instrumental

Paste a YouTube URL or upload an audio file, get the instrumental back (vocals removed). Runs locally.

It's glue: [yt-dlp](https://github.com/yt-dlp/yt-dlp) downloads the audio, [Demucs](https://github.com/adefossez/demucs) (`htdemucs_ft`, `--two-stems=vocals`) separates it, [Gradio](https://gradio.app) gives it a web UI. All in one `app.py`.

## Install

Needs Python 3.12, [ffmpeg](https://ffmpeg.org) and, for YouTube URLs, a JavaScript runtime yt-dlp accepts (Node 22+ or Deno) on your `PATH`. With asdf, the included `.tool-versions` selects Node 24.

```sh
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Run

```sh
.venv/bin/python app.py    # then open http://127.0.0.1:7860
```

The result is also saved as `output/htdemucs_ft/<song>/no_vocals.mp3` (with `vocals.mp3` next to it). The first run downloads the model weights (~300 MB).

## Model, speed, device

- `htdemucs_ft` is Demucs' best model for vocals; it's a bag of 4 models, so it's ~4x slower than `htdemucs`. Change `MODEL` in `app.py` if you want speed over quality.
- Device is picked automatically: CUDA, or MPS on Apple Silicon with **macOS 15+**, otherwise CPU. On macOS 14 MPS can't run htdemucs (it rejects conv outputs longer than 65536 samples), so it falls back to CPU.
- On an M1 CPU, `htdemucs_ft` processes roughly 1.5 s of audio per second per model, so a 4-minute song takes around 10 minutes.

## Use responsibly

YouTube's Terms of Service restrict downloading content. Only download what you have the right to. Separated tracks of copyrighted songs are for personal use (practice, karaoke at home), not for redistribution.

## License

MIT
