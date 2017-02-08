int reversePin = 11;
int forwardPin = 12;
int leftPin = 10;
int rightPin = 9;

int order = 55;
int time = 75;

  
int flag = 0;

void forward(int time){
  digitalWrite(forwardPin, LOW);
  delay(time);
  digitalWrite(forwardPin,HIGH);
}

void reverse(int time){
  digitalWrite(reversePin, LOW);
  delay(time);
  digitalWrite(reversePin,HIGH);
}

void left(int time){
  digitalWrite(leftPin, LOW);
  delay(time);
  digitalWrite(leftPin,HIGH);
}

void right(int time){
  digitalWrite(rightPin, LOW);
  delay(time);
  digitalWrite(rightPin,HIGH);
}

void leftTurnForward(int time){
  digitalWrite(forwardPin, LOW);
  digitalWrite(leftPin, LOW);
  delay(time);
  off();
}

void rightTurnForward(int time){
  digitalWrite(forwardPin, LOW);
  digitalWrite(rightPin, LOW);
  delay(time);
  off();
}

void leftTurnReverse(int time){
  digitalWrite(reversePin, LOW);
  digitalWrite(leftPin, LOW);
  delay(time);
  off();
}

void rightTurnReverse(int time){
  digitalWrite(reversePin, LOW);
  digitalWrite(rightPin, LOW);
  delay(time);
  off();
}

void off(){
  digitalWrite(forwardPin, HIGH);
  digitalWrite(leftPin, HIGH);
  digitalWrite(rightPin, HIGH);
  digitalWrite(reversePin, HIGH);
}

void orderControl(int order, int time){
  switch (order){
     case 0: off(); break;
   
     case 1: forward(time); order=0; break;
     case 2: reverse(time); order=0; break;
     case 4: right(time); order=0; break;
     case 8: left(time); order=0; break;
     
    
     case 5: rightTurnForward(time); order=0; break;
     case 9: leftTurnForward(time); order=0; break;
     case 6: rightTurnReverse(time); order=0; break;
     case 10: leftTurnReverse(time); order=0; break;
     

     default: off();
    } 
}

void setup() {                
  pinMode(rightPin, OUTPUT);     
  pinMode(leftPin, OUTPUT);
  pinMode(forwardPin, OUTPUT);
  pinMode(reversePin, OUTPUT);
  
  Serial.begin(115200);  
  Serial.print("\n\nStart...\n");
}

void loop() {
  off();

  if (Serial.available() > 0){
    order = Serial.read();
    Serial.print("Received: ");
    Serial.println(order);
    flag = 1;
  }
  
  if(flag){
    orderControl(order,time);
  }
 
}