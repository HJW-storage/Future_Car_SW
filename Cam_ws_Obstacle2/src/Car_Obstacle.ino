/*******************************************************
 * 쟁애물 회피 전용 아두이노 코드
*******************************************************/

#include <ros.h>
#include <ackermann_msgs/AckermannDriveStamped.h>
#include <PID_v1.h>
#include <Car_Library.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <std_msgs/Int16MultiArray.h>

int sub_speed = 0;
int sub_angle = 0;
/*--------------------------------------------------
                      ROSSETTING
---------------------------------------------------*/
std_msgs::Int16MultiArray str_msg;
ros::Publisher unochatter("uno", &str_msg);
ros::NodeHandle  nh;

void ackermannCallback(const ackermann_msgs::AckermannDriveStamped & ackermann);
ros::Subscriber<ackermann_msgs::AckermannDriveStamped> ackermannSubscriber("/ackermann_cmd", &ackermannCallback);

void motor_control(int speed, int angle);
void publishing_Rvalue();

/*--------------------------------------------------
                      INIT
---------------------------------------------------*/
int motor_speed = 0;
void ackermannCallback(const ackermann_msgs::AckermannDriveStamped & ackermann)
{
  sub_speed = ackermann.drive.speed;
  sub_angle = ackermann.drive.steering_angle;
  motor_speed = sub_speed;
}

String readString; //This while store the user input data

//resister value setting
//int R_value[4] = {0, 0, 0, 0};
int R_value[2] = {0, 0};
//int R_min = 103;
//int R_max = 187;
int R_min = 63;
int R_max = 217;
int R_mid = 151;
int R_now = 0;

int R_pin = A4;

// lane_angle range
const int MIN_LANE_ANGLE = -20;
const int MAX_LANE_ANGLE = 20;

//regarding PID
int REV = 0;          // Set point REQUIRED ENCODER VALUE

//motor PIN
int motorF1 = 3;  // steering
int motorF2 = 4;  // steering

int motorB1 = 6; // IN1, left
int motorB2 = 7; // IN2, left

// P 상수 정의
//const double kp = 0.5;
const double kp = 0.1;

double steering_output = 0.0;
double error = 0.0; 

int calculate_target_resistance(float lane_angle) {
  // 차선 각도를 가변저항 범위로 매핑
  int target_resistance = map(round(lane_angle), MIN_LANE_ANGLE, MAX_LANE_ANGLE, R_min, R_max);
  return target_resistance;
}


// 조향 제어 함수
double control_steering_based_on_lane_angle(int target_resistance, int current_resistance) {
    // 카메라에서 얻은 차선 각도를 이용해 목표 가변저항 값 계산 (비례 제어 사용)
    error = (target_resistance - current_resistance);
    double steering_output = kp * error;
    return steering_output;
}


void set_steering(float steering_output){
  float out = steering_output;
  float weight_multiplier = 5.0;
  
  if (out > 0) {
    if (out < 25){
      out = 25;
    }
    // 모터 좌회전
    motor_backward(motorF1, motorF2, out * weight_multiplier);
  }
  else if (out < 0) {
    if (out > -25){
      out = -25;
    }
    // 모터 우회전.
    motor_forward(motorF1, motorF2, abs(out) * weight_multiplier);
  }
  else {
    // 조향 출력이 0에 가까운 경우 모터를 정지 및 잠금
    motor_hold(motorF1, motorF2);
  }
}

/*--------------------------------------------------
                      SETUP
---------------------------------------------------*/
void setup() {
  nh.getHardware() -> setBaud(115200);
  nh.initNode();  

  nh.advertise(unochatter);
  nh.subscribe(ackermannSubscriber);

  TCCR2A = 2;            // Set CTC mode.  Same as TCCR2A = _BV(WGM21);
  TCCR2B = 6;            // Prescaler to divide by 32 (CS21 and CS20 only) 4-> by 64
  TCNT2 = 0;             // Clear the counter
  OCR2A = 249;           // Set for 1 msec rate
  TIMSK2 = 2;            // Set OCIE2A to begin counting with Compare A

  pinMode(R_pin, INPUT);
  
  pinMode(motorF1, OUTPUT);
  pinMode(motorF2, INPUT);
  
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, INPUT);
  motor_hold(motorF1, motorF2);
  
  //Serial.begin(9600); //initialize serial comunication

  TCCR1B = TCCR1B & 0b11111000 | 1;  // set 31KHz PWM to prevent motor noise
}
/*--------------------------------------------------
                      INTERUUPT
---------------------------------------------------*/

volatile int counter = 0; // 인터럽트 카운터 추가
const int read_interval = 2; // 읽기 간격 설정 (이 경우 5밀리초 마다 읽음)

ISR(TIMER2_COMPA_vect)
{
  counter++; // 인터럽트 카운터 증가

  // 주어진 간격마다 가변 저항 값을 읽음
  if (counter >= read_interval) {
    R_now = analogRead(R_pin) / 4;
    counter = 0; // 카운터 초기화
  }
}
/*--------------------------------------------------
                       LOOP
---------------------------------------------------*/
double out = 0.0 ;
void loop() {
  nh.spinOnce();
  
  publishing_Rvalue();  //rospub

  // 장애물 회피용 구동모터 제어
//  motor_control(motor_speed);
  motor_control_new(sub_angle);

  // right turn.
  // 모터의 오른쪽 회전에 문제가있음
  if (sub_angle > 0){
    REV = map (sub_angle, 0, 20, R_mid, R_max);
//    if (sub_angle > 10){
//      REV = R_max;
//    }
//    else{
//      REV = map (sub_angle, 0, 20, R_mid, R_max);
//    }
  }
  else if (sub_angle == 0){
    REV=R_mid;
  }
  // left turn.
  else if (sub_angle < 0){
    REV = map (sub_angle, -20, 0, R_min, R_mid);
  }
  
  steering_output = control_steering_based_on_lane_angle(REV, R_now);
  out = steering_output;
  
  float weight_multiple = 2.5;
  if (out > 0) {
    if (out < 25){
      out = 25;
    }
    // if REV > encoderValue motor move in forward direction.    ë§µí•‘ëœ ëª©í‘œê°’ì´ ì—”ì½”ë”ê°’ë³´ë‹¤ í¬ë©´ ì•žìœ¼ë¡œ ê°€ê³  (1ë²ˆì§¸ë¡œ ë°”ê¾¼ë‹¤)
    motor_backward(motorF1, motorF2, out * weight_multiple);         // Enabling motor enable pin to reach the desire angle                          // calling motor to move forward
  }
  else if (out < 0) {
    if (out > -25){
      out = -25;
      
    }
    motor_forward(motorF1, motorF2, abs(out) * weight_multiple);          // if REV < encoderValue motor move in forward direction.               ë§µí•‘ëœ ëª©í‘œê°’ì´ ì—”ì½”ë”ë³´ë‹¤ ìž‘ìœ¼ë©´ ë’¤ë¡œê°„ë‹¤.
    // calling motor to move reverse
  }
  else motor_hold(motorF1, motorF2);
}
/*--------------------------------------------------
                      FUNCTION
---------------------------------------------------*/

void pwmOut(double out) {
  float weight_multiplier = 2.5;
  if (out > 0) {
    if (out < 25){
      out = 25;
    }
    // if REV > encoderValue motor move in forward direction.    ë§µí•‘ëœ ëª©í‘œê°’ì´ ì—”ì½”ë”ê°’ë³´ë‹¤ í¬ë©´ ì•žìœ¼ë¡œ ê°€ê³  (1ë²ˆì§¸ë¡œ ë°”ê¾¼ë‹¤)
    motor_backward(motorF1, motorF2, out * weight_multiplier);         // Enabling motor enable pin to reach the desire angle                          // calling motor to move forward
  }
  else if (out < 0) {
    if (out > -25){
      out = -25;
      
    }
    motor_forward(motorF1, motorF2, abs(out) * weight_multiplier);          // if REV < encoderValue motor move in forward direction.               ë§µí•‘ëœ ëª©í‘œê°’ì´ ì—”ì½”ë”ë³´ë‹¤ ìž‘ìœ¼ë©´ ë’¤ë¡œê°„ë‹¤.
    // calling motor to move reverse
  }
  else motor_hold(motorF1, motorF2);
}

// 1.7 => max 100.3
// 1.8 => max 106.2
// 1.9 => max 112.1
// 2.0 => max 118
// 2.1 => max 123.9
// 2.2 => max 129.8
// 2.3 => max 135.7
// 2.4 => max 141.6
// 2.5 => max 147.5

void motor_control(int speed) {
  speed = speed * 3.0; 
  if (speed > 0) {
    motor_forward(motorB1, motorB2, speed);
  }
  else if (speed < 0){
    motor_backward(motorB1, motorB2, abs(speed));

  }
  else
    motor_hold(motorB1, motorB2);
}

void motor_control_new(float lane_angle) {
  int max_speed = 100; // 최대 속도를 100으로 설정합니다.
  float scaling_factor = 1.0; // 조향각 범위에 대한 스케일링 요소
  float normalized_angle = abs(lane_angle) / 20.0; // -20 ~ +20 범위를 0.0 ~ 1.0 범위로 정규화합니다.

  // 도로 중앙에서 가장 빠르게, 멀어질수록 속도 감소
  int speed = max_speed * (1.50 - (normalized_angle * scaling_factor));

  if (speed > 0) {
    if (speed == 50){
        motor_forward(motorB1, motorB2, 50);
      }
    else if(speed < 100){
      motor_forward(motorB1, motorB2, 75);
    }
    else{
        motor_forward(motorB1, motorB2, speed);
    }
  }
  else if (speed < 0) {
    motor_backward(motorB1, motorB2, abs(speed));
  }
  else {
    motor_hold(motorB1, motorB2);
  }
}


void publishing_Rvalue(){
  R_value[0] = R_now;
  R_value[1] = REV;
  R_value[2] = motor_speed;
//  R_value[3] = error;

  str_msg.data = R_value;
  str_msg.data_length = 3;
//  str_msg.data_length = 4;
  unochatter.publish( &str_msg );
}
