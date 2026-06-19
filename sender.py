# =============================================================
#  버스용 micro:bit  (송신기 / Transmitter)
#  - 기사님이 정류장 근처에서 A버튼을 누르면
#    "버스 도착" 신호를 무선(라디오)으로 발사한다.
#  - micro:bit 파일 이름은 반드시 main.py 로 저장해서 업로드.
# =============================================================
from microbit import *
import radio

# ---- 설정 ----------------------------------------------------
RADIO_GROUP = 7          # 송신기와 수신기의 그룹 번호가 같아야 통신됨!
SIGNAL = "BUS"           # 보낼 신호(약속된 단어)

# ---- 라디오 켜기 --------------------------------------------
radio.config(group=RADIO_GROUP, power=7)   # power 7 = 최대 출력(멀리 감)
radio.on()

# 평소(대기) 화면: 동쪽 화살표 = "준비됨"
display.show(Image.ARROW_E)

while True:
    # A버튼: 버스 도착 신호 1번 발사
    if button_a.was_pressed():
        radio.send(SIGNAL)
        display.show(Image.YES)   # 보냈다는 표시(체크)
        sleep(800)
        display.show(Image.ARROW_E)

    # B버튼: 통신 점검용(테스트). 같은 신호를 한 번 더 보냄.
    if button_b.was_pressed():
        radio.send(SIGNAL)
        display.show(Image.DIAMOND_SMALL)
        sleep(400)
        display.show(Image.ARROW_E)

    sleep(50)
