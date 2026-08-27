import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

def main():
    # I2C バスと PN532 の初期化
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    # ファームウェアバージョンの確認
    ic, ver, rev, support = pn532.firmware_version
    print(f"PN532を検出しました (FW v{ver}.{rev})")

    # SAM (Security Access Module) 設定を有効化
    pn532.SAM_configuration()

    print("\nNFC/RFIDカードをかざしてください...")

    try:
        while True:
            # カード（MIFARE / FeliCa / NFCタグなど）の読み取り試行
            uid = pn532.read_passive_target(timeout=0.5)

            if uid is not None:
                # 16進数文字列に変換 (例: 0x04 0xA1 0xB2 0xC3 -> 04a1b2c3)
                hex_uid = "".join([f"{i:02X}" for i in uid])
                print(f"カードを検出しました！ UID: {hex_uid}")
                
                # チャタリング防止のために少し待機
                time.sleep(1)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nプログラムを終了します。")

if __name__ == "__main__":
    main()