import os
import json
import time
import threading
import subprocess
import socket
import platform
import ntplib
import shutil
import requests
import socketio

from dotenv import load_dotenv
load_dotenv()

# Em Windows, usamos pywin32 para Named Pipes IPC
if platform.system() == "Windows":
    import win32file

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_ROOT = os.path.join(BASE_DIR, "videos")
BLANK_VIDEO = os.path.join(BASE_DIR, "blank.mp4")
NTP_SERVER = os.getenv("NTP_SERVER", "pool.ntp.org")
NTP_TIMEOUT = int(os.getenv("NTP_TIMEOUT", 2))
MAX_CACHED = int(os.getenv("MAX_CACHED_PROJECTS", 2))
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")
CLIENT_ID = socket.gethostname()

print(SERVER_URL)

# === IPC Socket por OS ===
if platform.system() == "Windows":
    IPC_PATH = fr"\\.\pipe\mpv-{CLIENT_ID}"
else:
    IPC_PATH = f"/tmp/mpv-{CLIENT_ID}.sock"

# === Inicia MPV com tela inicial ===
width, height = 480, 270
x_offset = 0
y_offset = 0

MPV_CMD = [
    "mpv",
    "--fs",
    "--no-terminal",
    "--loop=inf",
    "--idle=no",
    "--no-border", 
    "--force-window=yes",
    f"--input-ipc-server={IPC_PATH}",
    f"--geometry={width}x{height}+{x_offset}+{y_offset}",
    BLANK_VIDEO
]
if platform.system() != "Windows" and os.path.exists(IPC_PATH):
    os.remove(IPC_PATH)

print(f"[{CLIENT_ID}] Executando MPV: {' '.join(MPV_CMD)}")
subprocess.Popen(MPV_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.5)

# === Controlador IPC ===
class MPVController:
    def __init__(self, path):
        self.path = path

    def send(self, cmd):
        msg = json.dumps({"command": cmd}) + "\n"
        try:
            if platform.system() == "Windows":
                handle = win32file.CreateFile(
                    self.path,
                    win32file.GENERIC_WRITE,
                    0, None,
                    win32file.OPEN_EXISTING,
                    0, None
                )
                win32file.WriteFile(handle, msg.encode())
                win32file.CloseHandle(handle)
            else:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(self.path)
                s.sendall(msg.encode())
                s.close()
        except Exception as e:
            print(f"[{CLIENT_ID}] IPC erro: {e}")

controller = MPVController(IPC_PATH)

# === Função NTP ===
def get_ntp_time():
    try:
        return ntplib.NTPClient().request(NTP_SERVER, timeout=NTP_TIMEOUT).tx_time
    except:
        return time.time()

# === Monitor de drift ===
start_at = None
video_duration = None

def drift_monitor(interval=2):
    global start_at, video_duration
    ntp = ntplib.NTPClient()
    while True:
        time.sleep(interval)
        if start_at is None or video_duration is None:
            continue
        try:
            now_ntp = ntp.request(NTP_SERVER, timeout=NTP_TIMEOUT).tx_time
            elapsed = (now_ntp - start_at) % video_duration
            controller.send(["seek", elapsed, "absolute"])
        except Exception as e:
            print(f"[{CLIENT_ID}] drift erro: {e}")

threading.Thread(target=drift_monitor, daemon=True).start()

# === Limpa cache
def manter_cache(projeto):
    os.makedirs(CACHE_ROOT, exist_ok=True)  # ← garante que existe

    grupos = [f for f in os.listdir(CACHE_ROOT) if os.path.isdir(os.path.join(CACHE_ROOT, f))]
    if projeto in grupos:
        return
    while len(grupos) >= MAX_CACHED:
        grupo = grupos.pop(0)
        shutil.rmtree(os.path.join(CACHE_ROOT, grupo), ignore_errors=True)
        print(f"[CACHE] Projeto removido: {grupo}")
    os.makedirs(os.path.join(CACHE_ROOT, projeto), exist_ok=True)

# === Baixa vídeo
def baixar_video(grupo, nome, url):
    dst_path = os.path.join(CACHE_ROOT, grupo, nome)
    if os.path.exists(dst_path):
        return dst_path
    manter_cache(grupo)
    try:
        r = requests.get(url, stream=True)
        with open(dst_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[{CLIENT_ID}] Vídeo baixado: {nome}")
        return dst_path
    except Exception as e:
        print(f"[{CLIENT_ID}] Falha no download: {e}")
        return None

# === Socket.IO
sio = socketio.Client()

# === Tocar vídeo via IPC
def tocar_video(video, url, start_ts):
    global start_at, video_duration
    grupo = video.rsplit("_", 1)[0]
    caminho = baixar_video(grupo, video, url)
    if not caminho:
        return

    # Emit log após download
    sio.emit("log", {
        "client_id": CLIENT_ID,
        "msg": f"Vídeo baixado: {video}"
    })

    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            caminho
        ]).decode().strip()
        video_duration = float(out)
    except Exception as e:
        print(f"[{CLIENT_ID}] Erro duração: {e}")
        return

    start_at = float(start_ts)
    now = get_ntp_time()
    delay = start_at - now

    if delay > 0:
        msg = f"Aguardando {delay:.3f}s"
        print(f"[{CLIENT_ID}] {msg}")
        sio.emit("log", {"client_id": CLIENT_ID, "msg": msg})
        time.sleep(delay)

    msg = f"Tocando {video}"
    print(f"[{CLIENT_ID}] {msg}")
    sio.emit("log", {"client_id": CLIENT_ID, "msg": msg})

    controller.send(["loadfile", caminho, "replace"])

@sio.event
def connect():
    print(f"[{CLIENT_ID}] Conectado a {SERVER_URL}")
    sio.emit("status", {"client_id": CLIENT_ID})

@sio.on("play")
def on_play(data):
    print(f"[{CLIENT_ID}] play recebido: {data}")
    video = data.get("video")
    url = data.get("url")
    start_at = data.get("start_at")
    if video and url and start_at:
        threading.Thread(target=tocar_video, args=(video, url, start_at), daemon=True).start()

def loop_status():
    while True:
        sio.emit("status_atual", {"client_id": CLIENT_ID, "status": "idle"})
        time.sleep(1)

if __name__ == "__main__":
    try:
        sio.connect(SERVER_URL)
        threading.Thread(target=loop_status, daemon=True).start()
        sio.wait()
    except Exception as e:
        print(f"[{CLIENT_ID}] Socket falhou: {e}")
