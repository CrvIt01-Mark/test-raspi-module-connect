import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def main():

    # I2Cの設定 (128x64 解像度)
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

    # 画面のクリア
    oled.fill(0)
    oled.show()

    # 描画用のキャンバスを作成
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # テキストの描画
    font = ImageFont.load_default()
    draw.text((0, 0), "Hello, World!", font=font, fill=255)
    draw.text((0, 20), "Raspberry Pi", font=font, fill=255)
    draw.text((0, 40), "OLED Display", font=font, fill=255)

    # OLEDへ表示
    oled.image(image)
    oled.show()

    try:
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        oled.fill(0) #画面のクリア
        oled.show()
        print("\nプログラムを終了します。")

if __name__ == "__main__":
    main()
