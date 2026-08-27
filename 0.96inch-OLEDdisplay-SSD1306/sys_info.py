import time
import subprocess
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# --- OLED 初期化 (128x64 / I2C) ---
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

oled.fill(0)
oled.show()

# 描画キャンバスの準備
width = oled.width
height = oled.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

# 標準フォント
font = ImageFont.load_default()

def get_sys_info():
    """システム情報をシェルコマンド経由で取得"""
    # IPアドレスの取得
    try:
        cmd = "hostname -I | cut -d' ' -f1"
        ip = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if not ip:
            ip = "No Network"
    except Exception:
        ip = "Error"

    # CPU温度の取得
    try:
        cmd = "vcgencmd measure_temp | cut -d'=' -f2 | cut -d\"'\" -f1"
        temp = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        temp_str = f"{temp} C"
    except Exception:
        temp_str = "N/A"

    # メモリ使用量の取得
    try:
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.1f%%\", $3,$2,$3*100/$2 }'"
        mem = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    except Exception:
        mem = "Mem: N/A"

    # ディスク使用量の取得
    try:
        cmd = "df -h / | awk 'NR==2 {print $5}'"
        disk = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        disk_str = f"Disk: {disk}"
    except Exception:
        disk_str = "Disk: N/A"

    return ip, temp_str, mem, disk_str

print("Starting OLED Monitor... Press Ctrl+C to stop.")

try:
    while True:
        # 1. 画面のクリア（黒塗り）
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # 2. システム情報の取得
        ip, temp, mem, disk = get_sys_info()

        # 3. テキストの描画 (y座標を15pxずつズラして配置)
        draw.text((0, 0),  f"IP: {ip}", font=font, fill=255)
        draw.text((0, 16), f"CPU Temp: {temp}", font=font, fill=255)
        draw.text((0, 32), mem, font=font, fill=255)
        draw.text((0, 48), disk, font=font, fill=255)

        # 4. OLEDに描画を反映
        oled.image(image)
        oled.show()

        # 1秒待機
        time.sleep(1)

except KeyboardInterrupt:
    # 終了時に画面を消灯
    oled.fill(0)
    oled.show()
    print("\nMonitor stopped.")