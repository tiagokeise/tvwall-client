#!/bin/bash
set -e

echo "📦 Criando ambiente virtual, jovem..."
python3 -m venv venv

echo "🐍 Agora vou rodar o ambiente virtual e instalar as dependências, jovem..."
source venv/bin/activate
pip install --upgrade pip

echo "📄 Instalando as paradas do requirements.txt..."
pip install -r requirements.txt

echo "✅ Dependências na mão. Agora vamos configurar o ambiente."

echo "🌐 Qual é o endereço do servidor Socket.IO, jovem? (ex: http://192.168.0.193:5000)"
read -p "👉 Digita aqui: " SERVER_URL

echo "📝 Criando o .env com as configs padrão..."
cat <<EOF > .env
SERVER_URL=$SERVER_URL
NTP_SERVER=pool.ntp.org
NTP_TIMEOUT=2
MAX_CACHED_PROJECTS=2
TIME_SYNC=30
TIME_ONLINE=1
EOF

echo "✅ .env criado, jovem! Dá pra editar depois se precisar."

if [ -f "./setup_systemd.sh" ]; then
  echo "⚙️  Configurando o serviço no boot com o setup_systemd.sh, jovem..."
  chmod +x setup_systemd.sh
  ./setup_systemd.sh
else
  echo "❌ Jovem, não achei o setup_systemd.sh. Sem ele o serviço não vai subir no boot."
fi

# 🔁 Pergunta se quer reiniciar agora
read -p "🔁 Quer reiniciar agora pra testar tudo no boot? (s/n): " resp
if [[ "$resp" == "s" || "$resp" == "S" ]]; then
  echo "🕓 Beleza, jovem. Espera 5 segundos e já vai!"
  sleep 5
  sudo reboot
else
  echo "👌 Então reinicia depois com 'sudo reboot'. Tá nas suas mãos, jovem!"
fi