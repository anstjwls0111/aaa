# =====================================================================
#  발에 차는 스마트 안전 감지기 (어르신 낙상 예방용)
#  - 마이크로비트 MakeCode 파이썬
# ---------------------------------------------------------------------
#  [입력 센서]
#   1) 초음파 센서(HC-SR04) : 발 앞쪽 장애물까지 거리 측정 (메인)
#   2) 아날로그 광센서       : 어두울 때만 작동(낮엔 절전)
#  [출력 장치]
#   3) 부저(스피커)          : 가까울수록 빠르게 "삐…삐…삐삐삐"
#   4) RGB 네오픽셀 LED      : 평소 흰색으로 발밑 비춤 / 위험 시 빨강 깜빡
# ---------------------------------------------------------------------
#  [핀 연결]
#   - 초음파 Trig  -> P1
#   - 초음파 Echo  -> P2
#   - 광센서(아날로그) -> P0
#   - 네오픽셀 RGB LED -> P8
#   - 부저음        -> 마이크로비트 내장 스피커 사용
#
#  [확장 추가 필요] MakeCode 확장 검색창에서
#   - "sonar"     (초음파 센서)
#   - "neopixel"  (RGB LED)
#  를 추가해 주세요.
# =====================================================================

# ---- 거리 기준값(cm) : 3단계로 나눠 소리 속도를 바꿈 ----
DANGER = 15      # 아주 가까움 -> 빠른 삐삐삐 + 빨강 깜빡
WARN = 30        # 가까움(중간) -> 보통 속도
NOTICE = 60      # 이 거리보다 멀면 조용

# ---- 밝기 기준값 : 광센서 값이 이보다 작으면 '어두움(밤)' ----
DARK_LEVEL = 300   # 0(깜깜)~1023(아주 밝음), 현장에서 조정

# ---- RGB LED(네오픽셀) 4칸짜리 준비 ----
strip = neopixel.create(DigitalPin.P8, 4, NeoPixelMode.RGB)
strip.set_brightness(120)


def light_white():
    # 평소: 흰색으로 발밑 길 비추기
    strip.show_color(neopixel.colors(NeoPixelColors.WHITE))


def light_red():
    # 위험: 빨강
    strip.show_color(neopixel.rgb(255, 0, 0))


def light_off():
    strip.clear()
    strip.show()


def beep_once(length):
    # 짧은 경고음 1번 (length: 음 길이 ms)
    music.play_tone(988, length)


def on_forever():
    # 1) 밝기 확인 (낮/밤 판단)
    brightness = pins.analog_read_pin(AnalogPin.P0)

    if brightness > DARK_LEVEL:
        # 낮 -> 절전 모드 (아무것도 안 함)
        light_off()
        music.stop_all_sounds()
        basic.pause(500)
        return

    # 2) 밤 -> 켜짐, 평소엔 흰색으로 발밑 비춤
    light_white()

    # 3) 초음파로 앞쪽 거리 측정
    distance = sonar.ping(DigitalPin.P1, DigitalPin.P2, PingUnit.CENTIMETERS)

    # 측정 실패(0)이거나 멀면 -> 조용
    if distance == 0 or distance > NOTICE:
        basic.pause(100)

    # 가까움(중간) -> 느린 "삐 … 삐"
    elif distance > WARN:
        beep_once(120)
        basic.pause(400)

    # 더 가까움 -> 보통 속도 "삐..삐..삐"
    elif distance > DANGER:
        beep_once(120)
        basic.pause(150)

    # 아주 가까움 -> 빠른 "삐삐삐삐" + 빨강 깜빡 (자동차 후방감지기처럼)
    else:
        light_red()
        beep_once(80)
        basic.pause(40)
        light_white()   # 흰색<->빨강 번갈아 = 깜빡 효과
        basic.pause(40)


basic.forever(on_forever)
