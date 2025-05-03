# 🖥️ TVWall – Player Sincronizado para Videowall com Socket.IO

**TVWall** é um client Python desenvolvido para rodar em Raspberry Pi (ou qualquer Linux), que permite a exibição sincronizada de partes de um vídeo em múltiplas telas. Utiliza MPV como player, Socket.IO para comunicação em tempo real com o servidor, e NTP para sincronização precisa entre dispositivos.

---

## 📦 Funcionalidades

- 🎯 Sincronização de reprodução com precisão via NTP  
- 🔁 Reprodução contínua com `blank.mp4` até o comando do servidor  
- ⚡ Comunicação com servidor Flask via Socket.IO  
- 🧠 Download automático apenas da parte do vídeo atribuída ao player  
- 💾 Gerenciamento de cache com os últimos projetos baixados  
- ⚙️ Inicialização automática via `systemd`  

---

## 📁 Estrutura do projeto

```
tvwall/
├── blank.mp4                # Vídeo padrão (loop infinito até receber comando)
├── .env                     # Configurações de ambiente (URL do servidor, NTP, etc.)
├── player_socketio_sync.py  # Script principal do player
├── requirements.txt         # Dependências Python
├── install.sh               # Instala dependências e configura systemd
├── tvwall.service           # Serviço systemd para iniciar o player no boot
└── README.md
```

---

## 🚀 Instalação no Raspberry Pi

```bash
git clone https://github.com/tiagokeise/tvwall.git
cd tvwall
chmod +x install.sh
./install.sh
```

---

## ⚙️ Configuração

Edite o arquivo `.env` com as configurações do seu servidor:

```env
SERVER_URL=http://192.168.0.100:5000
NTP_SERVER=pool.ntp.org
NTP_TIMEOUT=2
MAX_CACHED_PROJECTS=2
```

---

## 🔄 Atualização

Para atualizar o player com alterações do repositório:

```bash
cd tvwall
git pull
sudo systemctl restart tvwall
```

---

## 🧪 Teste manual

```bash
python3 player_tvwall.py
```

---

## 🧷 Autor

Desenvolvido por [Tiago Keise](https://github.com/tiagokeise) para uso em instalações com múltiplos Raspberry Pi ou windows exibindo vídeos sincronizados.

---

## 📄 Licença

MIT
