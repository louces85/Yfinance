#!/bin/bash
# Remove tudo que foi instalado pelo install_whisper.sh

set -e

echo "=== 1. Removendo pacotes Python ==="
pip uninstall -y yt-dlp openai-whisper
echo "Python OK"

echo ""
echo "=== 2. Removendo modelos Whisper baixados (~/.cache/whisper) ==="
if [ -d "$HOME/.cache/whisper" ]; then
    rm -rf "$HOME/.cache/whisper"
    echo "Cache de modelos removido."
else
    echo "Nenhum cache encontrado."
fi

echo ""
echo "=== 3. Removendo ffmpeg (sistema) ==="
sudo apt remove -y ffmpeg
sudo apt autoremove -y
echo "ffmpeg OK"

echo ""
echo "=== Desinstalação concluída! ==="
