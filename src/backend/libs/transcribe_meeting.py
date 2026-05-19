#!/usr/bin/env python3
"""
Transcritor de reuniões do YouTube usando Whisper

INSTALAÇÃO:
    1. sudo apt update && sudo apt install -y ffmpeg
    2. pip install yt-dlp openai-whisper

USO:
    python transcribe_meeting.py "URL_DO_YOUTUBE"
    python transcribe_meeting.py "URL_DO_YOUTUBE" --model medium
    python transcribe_meeting.py "URL_DO_YOUTUBE" --model small --keep-audio

MODELOS DISPONÍVEIS (recomendado para sua RAM):
    tiny    ~390MB RAM  — rápido, qualidade básica
    base    ~550MB RAM  — boa velocidade
    small   ~2GB  RAM  — boa qualidade (RECOMENDADO)
    medium  ~5GB  RAM  — melhor qualidade (use só com RAM livre suficiente)
"""

import os
import sys
import argparse
import yt_dlp
import whisper
from pathlib import Path
from datetime import datetime

# Pasta de saída: um nível acima de backend/
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "knowledge_base"
TRANSCRICOES_DIR = KNOWLEDGE_BASE_DIR / "transcricoes"
AUDIO_TEMP_DIR = KNOWLEDGE_BASE_DIR / "audio_temp"


def download_audio(url: str) -> tuple:
    """Baixa o áudio do YouTube e retorna (caminho_arquivo, titulo)."""
    AUDIO_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": str(AUDIO_TEMP_DIR / "%(title)s.%(ext)s"),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info["title"]
        # yt-dlp pode gerar .mp3 ou .m4a dependendo do ffmpeg
        expected = ydl.prepare_filename(info)
        audio_path = Path(expected).with_suffix(".mp3")
        if not audio_path.exists():
            # Fallback: procura qualquer mp3 com o mesmo stem
            candidates = list(AUDIO_TEMP_DIR.glob(f"{Path(expected).stem}*"))
            if candidates:
                audio_path = candidates[0]

    return str(audio_path), title


def transcribe(audio_path: str, model_name: str) -> dict:
    """Carrega o modelo Whisper e transcreve o áudio."""
    print(f"\n[whisper] Carregando modelo '{model_name}'... (pode demorar na primeira vez)")
    model = whisper.load_model(model_name)
    print(f"[whisper] Transcrevendo: {audio_path}")
    result = model.transcribe(audio_path, language="en")
    return result


def save_transcription(result: dict, title: str) -> tuple:
    """Salva texto completo e versão com timestamps."""
    TRANSCRICOES_DIR.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{safe_title}__{timestamp}"

    # Texto limpo
    txt_path = TRANSCRICOES_DIR / f"{base_name}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Título: {title}\n")
        f.write(f"Data da transcrição: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(result["text"])

    # Com timestamps por segmento
    segments_path = TRANSCRICOES_DIR / f"{base_name}__timestamps.txt"
    with open(segments_path, "w", encoding="utf-8") as f:
        f.write(f"Título: {title}\n")
        f.write(f"Data da transcrição: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        for seg in result["segments"]:
            start = int(seg["start"])
            h, m, s = start // 3600, (start % 3600) // 60, start % 60
            f.write(f"[{h:02d}:{m:02d}:{s:02d}] {seg['text'].strip()}\n")

    return txt_path, segments_path


def main():
    parser = argparse.ArgumentParser(
        description="Transcreve vídeos do YouTube (reuniões Berkshire etc.) com Whisper"
    )
    parser.add_argument("url", help="URL do vídeo no YouTube")
    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium"],
        help="Modelo Whisper a usar (default: small)",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Manter o arquivo de áudio após a transcrição",
    )
    args = parser.parse_args()

    print(f"[yt-dlp] Baixando áudio de:\n  {args.url}\n")
    audio_path, title = download_audio(args.url)
    print(f"[yt-dlp] Áudio salvo: {audio_path}")

    result = transcribe(audio_path, args.model)

    txt_path, segments_path = save_transcription(result, title)

    print("\n✓ Transcrição concluída!")
    print(f"  Texto completo : {txt_path}")
    print(f"  Com timestamps : {segments_path}")

    if not args.keep_audio:
        try:
            os.remove(audio_path)
            print(f"  Áudio temp removido.")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
