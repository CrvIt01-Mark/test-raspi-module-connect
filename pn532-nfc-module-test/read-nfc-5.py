import subprocess
import os
import re
import time

TMP_FILE = "/home/shouji/python_project/pn532-nfc-module-test/nfc_out.txt"

def read_nfc_with_recovery():
    try:
        # nfc-list の出力をファイルへ落とす
        cmd = f"nfc-list > {TMP_FILE} 2>&1"
        subprocess.run(cmd, shell=True, timeout=10.0)
        
        if os.path.exists(TMP_FILE):
            with open(TMP_FILE, "r") as f:
                output = f.read()

            # チェックサムエラーやI/Oエラーが発生した場合のリカバリ判定
            if any(err in output for err in ["Input/output error", "Unable to open", "checksum mismatch"]):
                # エラー時はI2Cバスの復旧を待つため少し長めにウェイトを入れる
                time.sleep(2.0)
                return "ERROR", None

            # 1. ICOCA (FeliCa / Type F)
            felica_match = re.search(r'ID \(NFCID2\):\s+(([0-9A-Fa-f]{2}\s+){7}[0-9A-Fa-f]{2})', output)
            if felica_match:
                return "ICOCA (FeliCa)", felica_match.group(1).replace(' ', '').upper()

            # 2. 付属タグ (Type A)
            typea_match = re.search(r'UID \(NFCID1\):\s+(([0-9A-Fa-f]{2}\s+)+[0-9A-Fa-f]{2})', output)
            if typea_match:
                return "Type A タグ", typea_match.group(1).replace(' ', '').upper()

    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass

    return None, None

def main():
    print("=== ICOCA 安定読み取りシステム (リカバリ機能付き) ===")
    print("カードをかざしてください... (Ctrl+C で終了)\n")

    last_id = None
    last_time = 0

    while True:
        tag_type, tag_id = read_nfc_with_recovery()

        if tag_type == "ERROR":
            # ノイズ等でI2Cエラーが起きた場合はスキップしてループ継続
            time.sleep(2.0)
            continue

        if tag_id:
            current_time = time.time()
            if tag_id != last_id or (current_time - last_time) > 2.0:
                print(f"【検出成功】 種別: {tag_type} | ID: {tag_id}")
                last_id = tag_id
                last_time = current_time

        # I2C バス解放のための適切なインターバル
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n終了します。")