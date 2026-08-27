import time
from smartcard.Exceptions import NoCardException
from smartcard.System import readers
from smartcard.util import toHexString

r = readers()
if not r:
    print("カードリーダーが見つかりません")
    exit()

reader = r[0]
print(f"使用デバイス: {reader}")
print("ICカードをかざしてください... (Ctrl+C で終了)")

while True:
    try:
        connection = reader.createConnection()
        connection.connect()

        # PC/SC 共通の UID / IDm 取得コマンド (Get Data)
        GET_UID_CMD = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID_CMD)

        if sw1 == 0x90 and sw2 == 0x00:
            uid_hex = toHexString(data)
            byte_length = len(data)

            # 1. バイト長による一時判別
            if byte_length == 8:
                # FeliCa (IDmは必ず8バイト)
                card_type = "FeliCa (Suica / PASMO / nanaco / WAON / 一部社員証)"
                id_label = "IDm"
            elif byte_length == 4:
                # MIFARE Classic 1K/4K / NTAG (UIDは4バイト)
                card_type = "MIFARE / ISO 14443 Type A (4-byte UID)"
                id_label = "UID"
            elif byte_length == 7:
                # MIFARE Ultralight / DESFire (UIDは7バイト)
                card_type = "MIFARE / ISO 14443 Type A (7-byte UID)"
                id_label = "UID"
            else:
                card_type = f"未知のカード (UID長: {byte_length} bytes)"
                id_label = "ID/UID"

            print("----------------------------------------")
            print(f"判別結果 : {card_type}")
            print(f"  - {id_label}: {uid_hex} ({byte_length} bytes)")
            print("----------------------------------------")
        else:
            print("----------------------------------------")
            print(f"カード検出: 読み取りエラー (SW1={hex(sw1)}, SW2={hex(sw2)})")
            print("----------------------------------------")

        # 連続読み取り防止
        time.sleep(2)

    except NoCardException:
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n終了します")
        break
    except Exception as e:
        print(f"エラー: {e}")
        time.sleep(1)