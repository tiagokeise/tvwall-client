#!/bin/bash

SERVICE_NAME=tvwall
USER_NAME=ebc
WORK_DIR="/home/$USER_NAME/tvwall"
PYTHON_PATH="$WORK_DIR/venv/bin/python3"
SCRIPT_PATH="$WORK_DIR/player_tvwall.py"
ENV_PATH="$WORK_DIR/.env"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "🛠️ Criando serviço systemd: $SERVICE_NAME..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=tvwall video client
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$WORK_DIR
ExecStart=$PYTHON_PATH $SCRIPT_PATH
Restart=always
EnvironmentFile=$ENV_PATH

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Recarregando systemd e ativando serviço..."
sudo systemctl daemon-reexec
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "✅ Serviço $SERVICE_NAME instalado e iniciado."
echo "🔍 Veja logs com: journalctl -u $SERVICE_NAME -f"