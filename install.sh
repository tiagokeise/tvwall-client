#!/bin/bash

set -e

echo "📦 Criando ambiente virtual..."
python3 -m venv venv

echo "🐍 Ativando ambiente virtual e instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install python-socketio flask requests websocket-client

echo "✅ Dependências instaladas."

if [ ! -f ".env" ]; then
  echo "🌱 Criando .env de exemplo..."
  cat <<EOF > .env
SOCKET_SERVER=http://192.168.1.100:5000
CLIENT_ID=tv1
EOF
  echo "⚠️  Edite o arquivo .env para configurar o endereço do servidor e o ID deste Raspberry Pi."
fi

echo "✅ Instalação concluída. Agora você pode iniciar com:"
echo "  systemctl restart tvwall"
