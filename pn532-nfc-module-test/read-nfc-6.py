from smbus2 import SMBus, i2c_msg
import time
import re

I2C_BUS = 1
PN532_ADDR = 0x24  # PN532 I2C アドレス

def pn532_init(bus):
    """PN532 通常動作モード設定 (SAMConfiguration)"""
    try:
        # SAMConfiguration: Normal Mode (0x01)
        # 00 00 FF (Header) 03 FD (LEN, LCS) D4 14 01 (Data) 17 00 (DCS, Post)
        cmd = [0x00, 0x00, 0xFF, 0x03, 0xFD, 0xD4, 0x14, 0x01, 0x17, 0x00]
        bus.write_i2c_block_data(PN532_ADDR, 0x00, cmd)
        time.sleep(0.05)
    except Exception:
        pass

def send_command(bus, data):
    """PN532 へ正しく構造化されたコマンドフレームを送信"""
    # 構造: Preamble(00), Start(00 FF), LEN, LCS, [Data], DCS, Postamble(00)
    length = len(data)
    lcs = (~length + 1) & 0xFF  # 2's complement of length
    
    # Checksum (DCS) 計算
    dcs = (~sum(data) + 1) & 0xFF

    frame = [0x00, 0x00, 0xFF, length, lcs] + data + [dcs, 0x00]
    bus.write_i2c_block_data(PN532_ADDR, 0x00, frame)

def read_response(bus, timeout=0.2):
    """PN532 の Ready ステータス (0x01) を待ち受けてデータを受信"""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            # 64バイトのデータ受信リクエスト
            msg = i2c_msg.read(PN532_ADDR, 64)
            bus.i2c_rdwr(msg)
            res = list(msg)

            # 先頭バイト(data[0]) が 0x01 (Ready) になったら正常受信
            if len(res) > 0 and res[0] == 0x01:
                return res

        except Exception:
            pass

        time.sleep(0.01)  # 10ms 周期で Ready チェック

    return None

def read_icoca():
    """FeliCa (ICOCA) の IDm を正確に読み取る"""
    try:
        with SMBus(I2C_BUS) as bus:
            # FeliCa 212kbps ポーリングコマンド (InListPassiveTarget)
            # D4 4A (Command), 01 (1 card), 01 (212kbps FeliCa), 00 FF FF 00 00 (Payload)
            felica_cmd = [0xD4, 0x4A, 0x01, 0x01, 0x00, 0xFF, 0xFF, 0x00, 0x00]
            
            try:
                send_command(bus, felica_cmd)
            except IOError:
                pn532_init(bus)
                return None

            # PN532 の応答を最大 200ms 待機
            res = read_response(bus, timeout=0.2)

            if not res:
                return None

            hex_str = "".join([f"{b:02X}" for b in res])

            # FeliCa 応答パターン: D5 4C (または D5 4B) + ターゲット情報 + IDm (16文字/8バイト)
            match = re.search(r'D54[BC]0101([0-9A-Fa-f]{16})', hex_str)
            if match:
                return match.group(1)

    except Exception:
        pass

    return None

def main():
    print("=== PN532 I2C ICOCA Reader (通信同期対応版) ===")
    print("カードをかざしてください... (Ctrl+C で終了)\n")

    # 初期化
    try:
        with SMBus(I2C_BUS) as bus:
            pn532_init(bus)
    except Exception:
        print("【確認】PN532 の VCC(5V) ピンを一度抜き挿ししてください。")

    last_id = None
    last_time = 0

    while True:
        idm = read_icoca()

        if idm:
            current_time = time.time()
            if idm != last_id or (current_time - last_time) > 1.5:
                print(f"【成功】 ICOCA IDm: {idm}")
                last_id = idm
                last_time = current_time

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n終了します。")