import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_B

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    # SAM設定
    pn532.SAM_configuration()
    pn532.max_retries = 2

    print("=== カードスキャン開始 ===")
    print("1. 付属の白いカード / キーホルダー型タグ (Type A)")
    print("2. ICOCA / Suica / PASMO (FeliCa)")
    print("どちらかをかざしてください...\n")

    while True:
        try:
            # card_baud を明示して読み取り (0x00 = 106 kbps ISO14443A)
            uid = pn532.read_passive_target(card_baud=0x00, timeout=0.2)

            if uid is not None:
                hex_uid = "".join([f"{i:02X}" for i in uid])
                print(f"【検出成功】 UID / IDm: {hex_uid}")
                time.sleep(1.5)

        except RuntimeError:
            # 通信ノイズによるACK抜けはスキップ
            pass
        except KeyboardInterrupt:
            print("\n終了します。")
            break

        time.sleep(0.05)

if __name__ == "__main__":
    main()