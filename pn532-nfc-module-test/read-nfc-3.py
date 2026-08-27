import subprocess
import re
import time

def get_icoca_idm():
    """
    nfc-poll コマンドを実行し、出力から FeliCa の IDm (NFCID2) を抽出する
    """
    try:
        # nfc-poll コマンドを1回分実行（タイムアウト付き）
        result = subprocess.run(
            ['nfc-poll'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            timeout=1.5
        )
        
        output = result.stdout

        # 出力テキストの中から 'ID (NFCID2): XX XX XX ...' のパターンを探す
        match = re.search(r'ID \(NFCID2\):\s+(([0-9A-Fa-f]{2}\s+){7}[0-9A-Fa-f]{2})', output)
        if match:
            # スペースを除去して 16進数文字列にする (例: "012700123456789A")
            idm = match.group(1).replace(' ', '').upper()
            return idm

    except subprocess.TimeoutExpired:
        # カードがない場合のタイムアウト
        pass
    except Exception as e:
        print(f"エラー: {e}")

    return None

def main():
    print("=== ICOCA 読み取り開始 (libnfc連携) ===")
    print("カードをかざしてください... (Ctrl+C で終了)\n")

    while True:
        idm = get_icoca_idm()
        if idm:
            print(f"【ICOCA 検出成功】 IDm: {idm}")
            time.sleep(1.0)  # チャタリング防止
        
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n終了します。")