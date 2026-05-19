#!/bin/bash
# Instalação das dependências para transcrição com Whisper
# Execute uma vez antes de usar o transcribe_meeting.py

set -e

echo "=== 1. Instalando ffmpeg (sistema) ==="
sudo apt update && sudo apt install -y ffmpeg
echo "ffmpeg OK"

echo ""
echo "=== 2. Instalando dependências Python ==="
pip install yt-dlp openai-whisper
echo "Python OK"

echo ""
echo "=== Instalação concluída! ==="
echo ""
echo "Uso básico:"
echo "  python transcribe_meeting.py 'URL_DO_YOUTUBE'"
echo ""
echo "Com modelo medium (melhor qualidade, precisa de ~5GB RAM livre):"
echo "  python transcribe_meeting.py 'URL_DO_YOUTUBE' --model medium"
echo ""
echo "Manter o áudio após transcrição:"
echo "  python transcribe_meeting.py 'URL_DO_YOUTUBE' --keep-audio"
