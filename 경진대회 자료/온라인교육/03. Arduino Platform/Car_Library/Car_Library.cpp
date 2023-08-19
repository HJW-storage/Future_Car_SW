#include "Arduino.h"
#include "Car_Library.h"

float ultrasonic_distance(int trigPin, int echoPin)
{
    long distance, duration;

    digitalWrite(trigPin, LOW);
    digitalWrite(echoPin, LOW);
    delayMicroseconds(2);   // 최소 지연시간 - 부품 데이터 시트에 명시

    digitalWrite(trigPin, HIGH);    // 한 번 빵쏘고 
    delayMicroseconds(10);          // 최소지연시간 이후
    digitalWrite(trigPin, LOW);     // 다시 low로 끈다. 
    duration = pulseIn(echoPin, HIGH);  // pulseIn 아두이노 내장함수 -> 펄스의 High 구간을 측정. 
    distance = ((float)(340 * duration) / 1000) / 2;    

    return distance;
}   

int potentiometer_Read(int pin)
{
    int value;
    // value를 int형으로 선언했으므로 다음 작업이 필요하다.
    value = analogRead(pin) / 4; // 아날로그는 0~1023의 범위의 수로 표현되기에 4로 나누어 0~255로 만들어 디지털 값으로 대치한다.

    return value;
}

void motor_forward(int IN1, int IN2, int speed)
{
    // 전진 명령 - 배선을 잘 확인하자.
    analogWrite(IN1, speed);
    analogWrite(IN2, LOW);
}

void motor_backward(int IN1, int IN2, int speed)
{
    // 후진 명령 - 배선을 잘 확인하자.
    analogWrite(IN1, LOW);
    analogWrite(IN2, speed);
}

void motor_hold(int IN1, int IN2)
{
    // 정지 명령 - 모두 LOW
    analogWrite(IN1, LOW);
    analogWrite(IN2, LOW);
}