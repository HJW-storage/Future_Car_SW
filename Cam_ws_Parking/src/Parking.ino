#include <ros.h>
#include <ackermann_msgs/AckermannDriveStamped.h>
#include <PID_v1.h>
#include <Car_Library.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <std_msgs/UInt16.h>
#include <std_msgs/Int16MultiArray.h>
#include <std_msgs/Int32MultiArray.h>

/*--------------------------------------------------
                      ROSSETTING
---------------------------------------------------*/
std_msgs::Int16MultiArray str_msg;
ros::Publisher unochatter("uno", &str_msg);
ros::NodeHandle  nh;

long Ultra_value[6]={0,0,0,0,0,0};
std_msgs::Int32MultiArray sonic_msg;
ros::Publisher chatter("ultrasonic", &sonic_msg);

void ackermannCallback(const ackermann_msgs::AckermannDriveStamped & ackermann);
ros::Subscriber<ackermann_msgs::AckermannDriveStamped> ackermannSubscriber("/ackermann_cmd", &ackermannCallback);



/*--------------------------------------------------
                      INIT
---------------------------------------------------*/
int motor_speed = 0;
int motor_angle =0;
int sub_angle = 0;

//resister value setting
int R_value[2] = {0, 0};
int R_min = 63;
int R_max = 217;
int R_mid = 147;
int R_now = 0;
int R_pin = A4;

//regarding PID

int REV = 0;          // Set point REQUIRED ENCODER VALUE
//motor PIN
int motorB1 = 6; // IN1, left
int motorB2 = 7; // IN2, left

int motorF1 = 3; // IN1, right
int motorF2 = 4; // IN2, left

int echo1 = 28;
int trig1 = 29;

int echo2 = 48;
int trig2 = 49;

int echo3 = 50; // 34
int trig3 = 51; // 35

int echo4 = 36;
int trig4 = 37;

int echo5 = 38;
int trig5 = 39;

int echo6 = 42;
int trig6 = 43;


double kp = 0.05 , ki = 0.004, kd = 0.0;             // modify for optimal performance 변경해야하는 파라미터들
double input = 0, output = 0, setpoint = 0;
PID myPID(&input, &output, &setpoint, kp, ki, kd, DIRECT);
void motor_control(int speed);
void sonic_setup();
void get_sonic_data();
void publishing_Rvalue();

void ackermannCallback(const ackermann_msgs::AckermannDriveStamped & ackermann)
{
  int sub_speed = ackermann.drive.speed;
  int sub_angle = ackermann.drive.steering_angle;

  motor_angle = sub_angle;
  motor_control(sub_speed);
}
/*--------------------------------------------------
                      SETUP
---------------------------------------------------*/
void setup() {
  
  sonic_setup();
  nh.getHardware() -> setBaud(115200);
  nh.initNode();
  nh.advertise(unochatter);
  nh.subscribe(ackermannSubscriber);
  nh.advertise(chatter);

  TCCR2A = 2;            // Set CTC mode.  Same as TCCR2A = _BV(WGM21);
  TCCR2B = 5;            // Prescaler to divide by 32 (CS21 and CS20 only) 4-> by 64
  TCNT2 = 0;             // Clear the counter
  OCR2A = 249;           // Set for 1 msec rate
  TIMSK2 = 2;            // Set OCIE2A to begin counting with Compare A

  pinMode(R_pin, INPUT);
  
  pinMode(motorF1, OUTPUT);
  pinMode(motorF2, INPUT);
  
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, INPUT);

  motor_hold(motorF1, motorF2); // 처음 조향각 직진으로.

  //Serial.begin(9600); //initialize serial comunication

  TCCR1B = TCCR1B & 0b11111000 | 1;  // set 31KHz PWM to prevent motor noise
  myPID.SetMode(AUTOMATIC);   //set PID in Auto mode
  myPID.SetSampleTime(1);  // refresh rate of PID controller
  myPID.SetOutputLimits(-200, 200); // this is the MAX PWM value to move motor, here change in value reflect change in speed of motor.
//  myPID.SetOutputLimits(R_min, R_max); // this is the MAX PWM value to move motor, here change in value reflect change in speed of motor.
}
/*--------------------------------------------------
                      INTERUUPT
---------------------------------------------------*/

ISR(TIMER2_COMPA_vect)
{
  R_now = analogRead(R_pin)/4;
}

/*--------------------------------------------------
                       LOOP
---------------------------------------------------*/
void loop() {
  
  get_sonic_data();

  // steering angle calculate -------------------------------------------------------------------------
  if (sub_angle == 0){
      REV = R_mid;
  }
  else if (sub_angle > 0){
  // 우측 조향.
//    REV = map (motor_angle, 0, 20, R_mid, R_min); // mapping degree into pulse 입력받은 inputdata 각도를 펄스에 맵핑을 한다. (2번째 우리는 가벼저항값에 맵핑해야함 )
    REV = map (motor_angle, 0, 20, R_mid, R_max);
  } 
  else {
  // 왼쪽 조향. 
//    REV = map (motor_angle, -20, 0, R_max, R_mid);
    REV = map (motor_angle, -20, 0, R_min, R_mid);
  }
  // steering angle calculate -------------------------------------------------------------------------
  
  setpoint = REV;                    //PID while work to achive this value consider as SET value 맵핑된값을 셋포인트로 지정
  input = R_now ;           // data from encoder consider as a Process value 현재 엔코더값을 넣는다. -->이부분을 가변저항값으로 바꾼다

  publishing_Rvalue();  //rospub

  // steering motor ----------------------------------------------------------------------
  myPID.Compute();                 // calculate new output 계산한다-> 어떻게 계산하는지....
  if(motor_angle == -20){
    motor_backward(motorF1, motorF2, 90);
  }
  else if(motor_angle == 20){
    motor_forward(motorF1, motorF2, 90);
  }
  else {
//    motor_hold(motorF1, motorF2);
    pwmOut(output);
  }
  // steering motor ----------------------------------------------------------------------
  //motor_control(sub_speed);
  nh.spinOnce();

  // plot PID
//  Serial.print("ref : ");
//  Serial.println(motor_angle);
//
//  Serial.print("output : ");
//  Serial.println(output);
  
}

/*--------------------------------------------------
                      FUNCTION
---------------------------------------------------*/

void pwmOut(int out) {
  if (out > 0) {
    if (out < 50) {
      out = 50;
    }
    // if REV > encoderValue motor move in forward direction.    맵핑된 목표값이 엔코더값보다 크면 앞으로 가고 (1번째로 바꾼다)
    motor_backward(motorF1, motorF2, out);         // Enabling motor enable pin to reach the desire angle                          // calling motor to move forward
  }
  else if (out < 0) {
    if (out > -50) {
      out = -50;
    }
    motor_forward(motorF1, motorF2, abs(out));          // if REV < encoderValue motor move in forward direction.               맵핑된 목표값이 엔코더보다 작으면 뒤로간다.
    // calling motor to move reverse
  }
  else motor_hold(motorF1, motorF2);
}

void motor_control(int speed) {
  motor_speed = speed * 20;
  if (motor_speed > 0) {
    motor_forward(motorB1, motorB2, motor_speed);
  }
  else if (motor_speed < 0){
    motor_backward(motorB1, motorB2, abs(motor_speed));

  }
  else
    motor_hold(motorB1, motorB2);
 }


  
void sonic_setup(){
  pinMode(trig1, OUTPUT);
  pinMode(echo1, INPUT);
  
  pinMode(trig2, OUTPUT);
  pinMode(echo2, INPUT);
  
  pinMode(trig3, OUTPUT);
  pinMode(echo3, INPUT);
  
  pinMode(trig4, OUTPUT); 
  pinMode(echo4, INPUT);
  
  pinMode(trig5, OUTPUT);
  pinMode(echo5, INPUT);
  
  pinMode(trig6, OUTPUT);
  pinMode(echo6, INPUT);
}

void get_sonic_data(){
  // 오른쪽 뒤 
  int distance1 = ultrasonic_distance(trig1, echo1);
  Ultra_value[0]=distance1;

  // 오른쪽 중간
  int distance2 = ultrasonic_distance(trig2, echo2);
  Ultra_value[1]=distance2;

  // 오른쪽 앞
  int distance3 = ultrasonic_distance(trig3, echo3);
  Ultra_value[2]=distance3;

  // 왼쪽 뒤
  int distance4 = ultrasonic_distance(trig4, echo4);
  Ultra_value[3]=distance4;

  // 왼쪽 중간
  int distance5 = ultrasonic_distance(trig5, echo5);
  Ultra_value[4]=distance5;

  // 왼쪽 앞
  int distance6 = ultrasonic_distance(trig6, echo6);
  Ultra_value[5]=distance6;

Serial.print("Distance value1: ");
Serial.println(Ultra_value[0]);
Serial.print("Distance value2: ");
Serial.println(Ultra_value[1]);
Serial.print("Distance value3: ");
Serial.println(Ultra_value[2]);
Serial.print("Distance value4: ");
Serial.println(Ultra_value[3]);
Serial.print("Distance value5: ");
Serial.println(Ultra_value[4]);
Serial.print("Distance value6: ");
Serial.println(Ultra_value[5]);


 
sonic_msg.data = Ultra_value;
sonic_msg.data_length = 6;
chatter.publish( &sonic_msg );
nh.spinOnce();
}
void publishing_Rvalue(){
  R_value[0] = input;
  R_value[1] = REV;
  R_value[2] = output;
  str_msg.data = R_value;
  str_msg.data_length = 3;
  unochatter.publish( &str_msg );

//int R_min = 66;
//int R_max = 215;
//int R_mid = 150;
//int R_now = 0;
}
