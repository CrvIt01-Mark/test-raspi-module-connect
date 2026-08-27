import nfc

def on_connect(tag):
    # カードが接触した瞬間に呼ばれる関数
    # FeliCaカードの場合、tag.idm に IDm (バイト列) が格納されている
    if hasattr(tag, 'idm'):
        idm = tag.idm.hex().upper()
        print(f"【ICOCA 検出成功】 IDm: {idm}")
    else:
        print(f"その他のNFCタグを検出: {tag}")
    return True

def main():
    print("=== ICOCA 読み取り待機中 (nfcpy) ===")
    
    # Raspberry Pi の I2C-1 に繋がった PN532 を指定
    # (※環境によって 'tty:AMA0' や 'pn532:i2c:/dev/i2c-1' など)
    try:
        with nfc.ContactlessFrontend('pn532_i2c:/dev/i2c-1') as clf:
            while True:
                # カードが近づくのを待つ
                clf.connect(rdwr={'on-connect': on_connect})
                time.sleep(1.0)
    except Exception as e:
        print(f"接続エラー: {e}")

if __name__ == "__main__":
    main()