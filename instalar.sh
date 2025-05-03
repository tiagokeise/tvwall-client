#!/bin/bash

set -e

echo "📡 Iniciando instalação completa do tvwall-client no Raspberry Pi 3B..."

# 1. Atualiza o sistema
sudo apt update && sudo apt upgrade -y

# 2. Instala dependências necessárias
sudo apt install -y git python3 python3-pip python3-venv mpv

# 3. Cria o usuário 'ebc' se não existir
if ! id "ebc" &>/dev/null; then
  echo "👤 Criando usuário 'ebc'..."
  sudo adduser --disabled-password --gecos "" ebc
  sudo usermod -aG sudo ebc
fi

# 4. Clona o repositório para o diretório correto
sudo -u ebc bash <<'EOF'
cd /home/ebc
if [ ! -d "tvwall" ]; then
  echo "📁 Clonando repositório..."
  git clone https://github.com/tiagokeise/tvwall-client.git tvwall
fi
cd tvwall

# 5. Torna scripts executáveis
chmod +x install.sh setup_systemd.sh

# 6. Executa o install.sh como o próprio usuário
./install.sh
EOF

echo "✅ Sistema instalado com sucesso, jovem!"