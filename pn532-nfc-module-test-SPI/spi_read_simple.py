import time
import board
import busio
import digitalio
from adafruit_pn532.spi import PN532_SPI

# --- 初期化処理 ---
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = digitalio.DigitalInOut(board.D8)

pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print(f"PN532 接続完了: Firmware v{ver}.{rev}")

pn532.SAM_configuration()

print("\nNFCカードをタッチしてください... (Ctrl+C で終了)")

# --- 判定制御用の変数 ---
last_uid = None       # 前回読み取った一時UID
read_count = 0        # 同一UIDの連続一致カウント
processed_uid = None  # すでに処理済みのUID（かざしっぱなし検知用）

# 安定読み取りの設定値
REQUIRED_CONSECUTIVE_READS = 2  # 確定に必要な連続一致回数
INTERVAL_SEC = 0.1              # チャック間隔（秒）

try:
    while True:
        # カードを検知 (タイムアウトは短めの 0.2 秒に設定)
        uid = pn532.read_passive_target(timeout=0.2)

        if uid is not None:
            current_uid = "".join([f"{x:02X}" for x in uid])

            # すでに処理済みのカードがかざされたままの場合は無視
            if current_uid == processed_uid:
                time.sleep(INTERVAL_SEC)
                continue

            # 直前と同じ UID が読めたか判定
            if current_uid == last_uid:
                read_count += 1
            else:
                # 別の UID が読めた、または不安定な場合はカウントリセット
                last_uid = current_uid
                read_count = 1

            # 設定回数（2回）連続で同じ UID が読めた場合「確定」とする
            if read_count >= REQUIRED_CONSECUTIVE_READS:
                print(f"\n[確定] 正確に読み取りました: {current_uid}")
                
                # --------------------------------------------------
                # ここに確定時の処理を記述（照合・リレー制御・ログ記録など）
                # --------------------------------------------------

                # 確定した UID を記憶し、同一カードのかざしっぱなしによる連続動作を防ぐ
                processed_uid = current_uid
                last_uid = None
                read_count = 0

        else:
            # カードが離された（または通信失敗）場合は状態をリセット
            if processed_uid is not None:
                print(">> カードが離されました。")
            
            last_uid = None
            read_count = 0
            processed_uid = None

        time.sleep(INTERVAL_SEC)

except KeyboardInterrupt:
    print("\nプログラムを終了します。")