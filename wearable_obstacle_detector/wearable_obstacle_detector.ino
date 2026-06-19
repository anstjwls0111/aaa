/*
 * 웨어러블 장애물 감지 장치 (어르신 낙상 예방)
 *
 * [핀 배치]
 *   초음파 TRIG  → 2번 핀
 *   초음파 ECHO  → 3번 핀
 *   부저         → 4번 핀  (액티브 부저)
 *   광센서(CDS)  → A0 핀
 *   RGB LED R    → 9번 핀  (PWM)
 *   RGB LED G    → 10번 핀 (PWM)
 *   RGB LED B    → 11번 핀 (PWM)
 *
 * [작동 흐름]
 *   낮 (광센서 밝음) → 절전 모드 (모두 OFF)
 *   밤 (광센서 어두움) →
 *     거리 > 50cm  : 안전 – LED 흰색, 부저 OFF
 *     20~50cm      : 경고 – LED 흰색, 부저 느리게 삐…삐…
 *     거리 < 20cm  : 위험 – LED 빨강 깜빡, 부저 빠르게 삐삐삐삐
 */

// ─── 핀 정의 ─────────────────────────────────────────────
#define TRIG_PIN      2
#define ECHO_PIN      3
#define BUZZER_PIN    4
#define LIGHT_PIN     A0
#define LED_R_PIN     9
#define LED_G_PIN     10
#define LED_B_PIN     11

// ─── 임계값 ──────────────────────────────────────────────
// 광센서: 값이 낮을수록 어두움. 400 이하면 야간으로 판단
// 실제 환경에 따라 조절 (Serial Monitor로 확인 후 조정)
#define LIGHT_THRESHOLD   400

#define DIST_DANGER   20    // cm – 이하면 위험
#define DIST_WARN     50    // cm – 이하면 경고

// ─── 부저 타이밍 (ms) ────────────────────────────────────
#define BEEP_DANGER_ON    80
#define BEEP_DANGER_OFF   80
#define BEEP_WARN_ON      250
#define BEEP_WARN_OFF     500

// ─── 전역 변수 ───────────────────────────────────────────
unsigned long lastBeepTime = 0;
bool buzzerState = false;   // true = 현재 ON

// ─── LED 색상 설정 (RGB 0~255, 공통 음극 기준) ──────────
void setLED(int r, int g, int b) {
  analogWrite(LED_R_PIN, r);
  analogWrite(LED_G_PIN, g);
  analogWrite(LED_B_PIN, b);
}

// ─── 모든 출력 끄기 ──────────────────────────────────────
void allOff() {
  setLED(0, 0, 0);
  digitalWrite(BUZZER_PIN, LOW);
  buzzerState = false;
}

// ─── 초음파 거리 측정 (cm) ───────────────────────────────
// 반환값: 측정 거리(cm), 신호 없으면 999 반환
long measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // timeout 25ms → 최대 약 425cm까지 측정
  long duration = pulseIn(ECHO_PIN, HIGH, 25000);
  if (duration == 0) return 999;
  return duration * 17L / 1000;  // (duration * 0.034 / 2) 정수 근사
}

// ─── 비차단 방식 부저 제어 ───────────────────────────────
// delay() 없이 millis() 기반으로 ON/OFF 반복
void updateBuzzer(unsigned int onDur, unsigned int offDur) {
  unsigned long now = millis();
  if (buzzerState) {
    if (now - lastBeepTime >= onDur) {
      digitalWrite(BUZZER_PIN, LOW);
      buzzerState = false;
      lastBeepTime = now;
    }
  } else {
    if (now - lastBeepTime >= offDur) {
      digitalWrite(BUZZER_PIN, HIGH);
      buzzerState = true;
      lastBeepTime = now;
    }
  }
}

// ─── setup ───────────────────────────────────────────────
void setup() {
  pinMode(TRIG_PIN,   OUTPUT);
  pinMode(ECHO_PIN,   INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R_PIN,  OUTPUT);
  pinMode(LED_G_PIN,  OUTPUT);
  pinMode(LED_B_PIN,  OUTPUT);

  Serial.begin(9600);
  allOff();
  Serial.println("=== 웨어러블 장애물 감지 장치 시작 ===");
}

// ─── loop ────────────────────────────────────────────────
void loop() {
  int lightValue = analogRead(LIGHT_PIN);

  // ── 낮 (밝음) → 절전 모드 ──────────────────────────────
  if (lightValue > LIGHT_THRESHOLD) {
    allOff();
    Serial.print("낮 모드 (절전) | 광센서: ");
    Serial.println(lightValue);
    delay(500);
    return;
  }

  // ── 밤 (어두움) → 장애물 감지 모드 ─────────────────────
  long dist = measureDistance();

  Serial.print("광센서: ");
  Serial.print(lightValue);
  Serial.print(" | 거리: ");
  Serial.print(dist);
  Serial.print("cm | 상태: ");

  if (dist <= DIST_DANGER) {
    // 위험: 빠른 부저 + 빨강 LED 깜빡임
    Serial.println("위험!");
    updateBuzzer(BEEP_DANGER_ON, BEEP_DANGER_OFF);
    // LED는 부저와 함께 깜빡 (buzzerState와 동기화)
    setLED(buzzerState ? 255 : 0, 0, 0);

  } else if (dist <= DIST_WARN) {
    // 경고: 느린 부저 + 흰색 LED
    Serial.println("경고");
    updateBuzzer(BEEP_WARN_ON, BEEP_WARN_OFF);
    setLED(180, 180, 180);

  } else {
    // 안전: 무음 + 흰색 LED (발밑 조명)
    Serial.println("안전");
    digitalWrite(BUZZER_PIN, LOW);
    buzzerState = false;
    setLED(200, 200, 200);
  }

  delay(10);  // CPU 부담 완화
}
