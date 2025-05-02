#!/bin/bash

echo "[INSTALL] Atualizando pacotes..."
sudo apt update
sudo apt install -y python3-pip mpv ffmpeg

echo "[INSTALL] Instalando dependências Python..."
pip3 install -r requirements.txt

echo "[INSTALL] Copiando systemd service para o boot..."
sudo cp tvwall.service /etc/systemd/system/tvwall.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable tvwall.service

echo "[INSTALL] Pronto! Use 'sudo systemctl start tvwall' para iniciar o player."