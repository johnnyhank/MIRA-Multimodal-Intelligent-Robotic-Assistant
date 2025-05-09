import os
import socket
import time
import pygame
from datetime import datetime

LOG_PATH = "./speak_ip.log"
VOICE_DIR = "./voice"

def log(msg, max_lines=50):
    now = f"[{datetime.now()}] {msg}\n"
    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()[-(max_lines - 1):]
        else:
            lines = []
        lines.append(now)
        with open(LOG_PATH, "w") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"日志写入失败: {e}")

def wait_for_audio_device(timeout=25):
    log("🕒 正在等待音频设备初始化...")
    start = time.time()
    attempt = 1
    while time.time() - start < timeout:
        try:
            log(f"🧪 第 {attempt} 次尝试初始化 pygame.mixer")
            pygame.mixer.init()
            pygame.mixer.quit()
            log("✅ 音频设备已就绪")
            return True
        except Exception as e:
            log(f"❌ 尝试失败: {e}")
            time.sleep(1)
            attempt += 1
    log("❌ 超时未检测到音频设备，放弃播报")
    return False

def get_local_ip(retries=5, delay=3):
    for attempt in range(retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("114.114.114.114", 0))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        if ip != "127.0.0.1":
            return ip
        log(f"⚠️ 第 {attempt+1}/{retries} 次尝试获取IP失败，稍后重试...")
        time.sleep(delay)
    log("❌ 最终仍获取不到有效IP，使用127.0.0.1")
    return "127.0.0.1"

def play_sound(name):
    path = os.path.join(VOICE_DIR, f"{name}.mp3")
    log(f"🔊 尝试播放: {path}")
    if not os.path.exists(path):
        log(f"❌ 找不到语音文件: {path}")
        return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.9)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
    except Exception as e:
        log(f"❌ 播放失败: {e}")

if __name__ == '__main__':
    try:
        log("🚀 脚本启动")

        # os.environ["SDL_AUDIODRIVER"] = "alsa"
        os.environ["AUDIODEV"] = "hw:0,0"

        if not wait_for_audio_device():
            exit(1)

        ip = get_local_ip()
        log(f"📡 获取IP: {ip}")

        if os.path.exists(os.path.join(VOICE_DIR, "启动成功.mp3")):
            play_sound("启动成功")

        if ip == "127.0.0.1":
            if os.path.exists(os.path.join(VOICE_DIR, "网络异常.mp3")):
                play_sound("网络异常")
            log("⚠️ IP 无效，已播报网络异常")
        else:
            play_sound("IP地址为")
            for ch in ip:
                if ch == ".":
                    play_sound("点")
                elif ch.isdigit():
                    play_sound(ch)

        log("✅ 播报完成")

    except Exception as e:
        log(f"🔥 脚本顶层错误: {e}")
