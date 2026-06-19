# =============================================================
#  정류장용 micro:bit  (수신기 / Receiver) - 내장 LED 화면 버전
#  - 추가 부품 없이 micro:bit 1개로 바로 동작하는 기본 버전.
#  - 신호를 받으면: 글자(내장 5x5 LED) + 부저(삑삑삑) + RGB LED 깜빡임
#  - 밤(어두움)이면: 광센서가 감지해서 RGB LED로 정류장을 밝힌다.
#  - micro:bit 파일 이름은 반드시 main.py 로 저장해서 업로드.
#
#  [배선]  (Grove 모듈 기준, 핀 번호는 환경에 맞게 바꿔도 됨)
#    - 부저(Buzzer)        : P0
#    - 광센서(Light)       : P1  (아날로그)
#    - RGB 레인보우 LED    : P2  (네오픽셀/WS2812)
# =============================================================
from microbit import *
import radio
import music
import neopixel

# ---- 설정 (현장에 맞게 숫자만 바꾸면 됨) --------------------
RADIO_GROUP   = 7      # 송신기와 같은 그룹 번호
SIGNAL        = "BUS"  # 약속된 신호
DARK_LEVEL    = 200    # 이 값보다 어두우면 '밤'으로 판단 (0~1023)
ALERT_SECONDS = 30     # 버스 도착 알림을 보여주는 시간(초)
NUM_LEDS      = 8      # RGB 레인보우 LED 개수
REBEEP_MS     = 5000   # 알림 중 다시 삑삑 울리는 간격(밀리초)

# ---- 핀/장치 ------------------------------------------------
BUZZER_PIN = pin0
LIGHT_PIN  = pin1
np = neopixel.NeoPixel(pin2, NUM_LEDS)

radio.config(group=RADIO_GROUP)
radio.on()


# ---- 도우미 함수 --------------------------------------------
def light_value():
    """광센서 값 읽기 (작을수록 어두움)"""
    return LIGHT_PIN.read_analog()


def is_night():
    return light_value() < DARK_LEVEL


def leds_fill(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.show()


def leds_off():
    leds_fill(0, 0, 0)


def beep_alert():
    """삑삑삑 알림음 (눈이 어두워도 귀로 확인)"""
    for _ in range(3):
        music.pitch(988, 150, BUZZER_PIN)  # 높은 '시' 음
        sleep(120)


# ---- 화면 상태 관리 -----------------------------------------
# display.scroll(... wait=False, loop=True) 는 배경에서 계속 흐른다.
# 같은 상태를 매번 다시 호출하지 않도록 현재 상태를 기억한다.
STATE_IDLE = 0
STATE_ALERT = 1
screen_state = None


def set_idle_screen():
    global screen_state
    if screen_state != STATE_IDLE:
        screen_state = STATE_IDLE
        display.scroll("BUS STOP", wait=False, loop=True, delay=120)


def set_alert_screen():
    global screen_state
    if screen_state != STATE_ALERT:
        screen_state = STATE_ALERT
        display.scroll("BUS COMING", wait=False, loop=True, delay=90)


# ---- 시작 상태 ----------------------------------------------
set_idle_screen()
alert_until = 0          # 이 시각(ms)까지 알림 모드 유지
last_beep = 0
last_blink = 0
blink_on = False

# ---- 메인 반복 ----------------------------------------------
while True:
    now = running_time()

    # 1) 신호 수신 확인
    msg = radio.receive()
    if msg == SIGNAL:
        alert_until = now + ALERT_SECONDS * 1000
        set_alert_screen()
        beep_alert()
        last_beep = now

    alerting = now < alert_until
    night = is_night()

    # 2) 알림 모드일 때
    if alerting:
        set_alert_screen()

        # 일정 간격으로 다시 삑삑
        if now - last_beep > REBEEP_MS:
            beep_alert()
            last_beep = now

        # RGB LED 깜빡여서 강조 (밤이면 더 밝게)
        if now - last_blink > 300:
            last_blink = now
            blink_on = not blink_on
            if blink_on:
                leds_fill(60, 0, 0) if not night else leds_fill(120, 0, 0)
            else:
                # 밤이면 꺼지지 않고 은은한 조명 유지, 낮이면 완전히 끔
                leds_fill(40, 25, 0) if night else leds_off()

    # 3) 평소 모드일 때
    else:
        set_idle_screen()
        if night:
            leds_fill(40, 25, 0)   # 밤: 따뜻한 색으로 정류장 조명
        else:
            leds_off()             # 낮: 끔

    sleep(50)
