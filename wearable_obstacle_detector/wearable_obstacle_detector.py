from microbit import *
import utime

# ── 핀 설정 ──────────────────────────────────────────────
# P0: HC-SR04 TRIG  (디지털 출력)
# P1: HC-SR04 ECHO  (디지털 입력)
# P2: CDS 광센서    (아날로그 입력, 10kΩ 풀다운 분압회로)
# P8: 액티브 부저   (디지털 출력)
# P12: RGB LED 빨강 (디지털 출력)
# P13: RGB LED 초록 (디지털 출력)
# P14: RGB LED 파랑 (디지털 출력)

TRIG   = pin0
ECHO   = pin1
LIGHT  = pin2
BUZZER = pin8
LED_R  = pin12
LED_G  = pin13
LED_B  = pin14

# ── 임계값 설정 ───────────────────────────────────────────
# 광센서: read_analog() → 0~1023
#   어두울수록 CDS 저항↑ → 분압 전압↓ → 값 작아짐
#   400 미만이면 야간으로 판단 (환경에 따라 조절)
LIGHT_THRESHOLD = 400

DIST_DANGER = 20    # cm 이하: 위험 구간
DIST_WARN   = 50    # cm 이하: 경고 구간

# ── 부저 점멸 간격 (ms) ───────────────────────────────────
BEEP_DANGER_ON  = 80     # 위험: 빠른 삐삐삐
BEEP_DANGER_OFF = 80
BEEP_WARN_ON    = 250    # 경고: 느린 삐… 삐…
BEEP_WARN_OFF   = 500

# ── 전역 상태 변수 ────────────────────────────────────────
buzzer_state   = False
last_beep_time = 0


def measure_distance():
    """HC-SR04 초음파 센서로 거리 측정 (cm). 신호 없으면 999 반환."""
    TRIG.write_digital(0)
    utime.sleep_us(2)
    TRIG.write_digital(1)
    utime.sleep_us(10)
    TRIG.write_digital(0)

    # ECHO 신호 HIGH 될 때까지 대기 (최대 30ms)
    timeout = running_time() + 30
    while ECHO.read_digital() == 0:
        if running_time() > timeout:
            return 999

    start = utime.ticks_us()

    # ECHO 신호 LOW 될 때까지 대기 (최대 25ms)
    while ECHO.read_digital() == 1:
        if utime.ticks_diff(utime.ticks_us(), start) > 25000:
            return 999

    duration = utime.ticks_diff(utime.ticks_us(), start)
    return duration * 17 // 1000   # μs → cm 변환 (340m/s ÷ 2)


def set_led(r, g, b):
    """RGB LED 색상 설정. 공통 음극(Common Cathode) 기준: 1=ON, 0=OFF"""
    LED_R.write_digital(r)
    LED_G.write_digital(g)
    LED_B.write_digital(b)


def all_off():
    """모든 출력 끄기 (절전 모드 진입 시 호출)"""
    global buzzer_state
    set_led(0, 0, 0)
    BUZZER.write_digital(0)
    display.clear()
    buzzer_state = False


def update_buzzer(on_dur, off_dur):
    """running_time() 기반 비차단 부저 제어.
    delay() 없이 LED와 동시에 동작하도록 비동기 방식 사용."""
    global buzzer_state, last_beep_time
    now = running_time()
    if buzzer_state:
        if now - last_beep_time >= on_dur:
            BUZZER.write_digital(0)
            buzzer_state = False
            last_beep_time = now
    else:
        if now - last_beep_time >= off_dur:
            BUZZER.write_digital(1)
            buzzer_state = True
            last_beep_time = now


# ── 초기화 ───────────────────────────────────────────────
all_off()
display.scroll("READY", delay=80)

# ── 메인 루프 ─────────────────────────────────────────────
while True:
    light_val = LIGHT.read_analog()    # 0~1023

    # ── 낮 (밝음) → 절전 모드 ──────────────────────────────
    if light_val >= LIGHT_THRESHOLD:
        all_off()
        display.show(Image.ASLEEP)
        sleep(500)
        continue

    # ── 밤 (어두움) → 장애물 감지 모드 ─────────────────────
    dist = measure_distance()

    if dist <= DIST_DANGER:
        # 위험: 빠른 부저 + 빨강 LED 깜빡 + X 표시
        update_buzzer(BEEP_DANGER_ON, BEEP_DANGER_OFF)
        if buzzer_state:
            set_led(1, 0, 0)
            display.show(Image.NO)
        else:
            set_led(0, 0, 0)
            display.clear()

    elif dist <= DIST_WARN:
        # 경고: 느린 부저 + 흰색 LED + 아래 화살표
        update_buzzer(BEEP_WARN_ON, BEEP_WARN_OFF)
        set_led(1, 1, 1)
        display.show(Image.ARROW_S)

    else:
        # 안전: 무음 + 흰색 LED (발밑 조명) + 하트
        BUZZER.write_digital(0)
        buzzer_state = False
        set_led(1, 1, 1)
        display.show(Image.HEART)

    sleep(10)
