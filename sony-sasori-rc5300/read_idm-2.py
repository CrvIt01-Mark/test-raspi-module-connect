import time
from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.System import readers
from smartcard.util import toHexString

r = readers()
if not r:
    print("カードリーダーが見つかりません")
    exit()

reader = r[0]
print(f"使用デバイス: {reader}")
print("FeliCaカード（Suica / PASMO等）をかざしてください... (Ctrl+C で終了)\n")

# 前回読み取ったIDmを保持（同じカードの連続検知を防止するため）
last_idm = None

while True:
    try:
        connection = reader.createConnection()
        connection.connect()

        # UID/IDm 取得コマンド (APDU)
        GET_UID_CMD = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID_CMD)

        if sw1 == 0x90 and sw2 == 0x00:
            byte_length = len(data)

            # ----------------------------------------------------
            # 【判定処理】 8バイト（FeliCa）以外は無視してリトライ
            # ----------------------------------------------------
            if byte_length != 8:
                # MIFAREなどの場合
                print(
                    f" [無視] FeliCa以外のカードを検知しました (UID長: {byte_length} bytes) -> リトライ中...",
                    end="\r",
                )
                time.sleep(0.5)
                continue

            # FeliCa（8バイト）の場合のみ以下の処理を実行
            idm_hex = toHexString(data)

            # 連続読み取り防止（同じカードが載り続けている場合は表示しない）
            if idm_hex != last_idm:
                print("\n========================================")
                print("【FeliCa検知成功】")
                print(f"  IDm : {idm_hex}")
                print("========================================")
                last_idm = idm_hex

        time.sleep(1)

    except NoCardException:
        # カードが離されたら直前のIDm記録をリセット
        last_idm = None
        # 画面の無視メッセージ等をクリアするための表示補助
        print(" カード待機中...                                 ", end="\r")
        time.sleep(0.3)

    except CardConnectionException:
        # 重ね読みによる電波衝突（コリジョン）で通信エラーが起きた場合
        print(" [警告] 電波干渉または読み取りエラー -> リトライ中...", end="\r")
        time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n\n終了します")
        break

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        time.sleep(1)