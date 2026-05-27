#include <ESP32Servo.h>

// Definição dos pinos físicos atualizada (Pan alterado para o pino 18)
const int pinServoPan = 18;  // Eixo Horizontal (Esquerda/Direita) - Conecte no pino 18
const int pinServoTilt = 23; // Eixo Vertical (Cima/Baixo) - Conecte no pino D23

Servo servoPan;
Servo servoTilt;

// Posições iniciais (centro)
int posPan = 90;
int posTilt = 90;

// Variáveis para o parser serial não-bloqueante
String comandoBuffer = "";
bool comandoCompleto = false;

void setup() {
  Serial.begin(115200);
  
  // ALOCAÇÃO DE TIMERS (Crucial para a estabilidade da biblioteca ESP32Servo em algumas placas)
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  // Configuração padrão dos servos
  servoPan.setPeriodHertz(50);
  servoTilt.setPeriodHertz(50);
  
  servoPan.attach(pinServoPan, 500, 2400);
  servoTilt.attach(pinServoTilt, 500, 2400);
  
  // Centraliza inicialmente
  servoPan.write(posPan);
  servoTilt.write(posTilt);
  delay(500);

  // --- SEQUÊNCIA DE AUTOTESTE DE INICIALIZAÇÃO INDIVIDUAL ---
  Serial.println("Iniciando autoteste dos motores de forma sequencial...");
  
  // 1. Testa individualmente o Servo Pan (Esquerda/Direita)
  Serial.println("[AUTOTESTE] Movendo Servo Pan (Esquerda/Direita) -> pino 18...");
  servoPan.write(0);   // Vai para a esquerda total
  delay(800);
  servoPan.write(180); // Vai para a direita total
  delay(800);
  servoPan.write(90);  // Volta ao centro
  delay(800);
  
  // 2. Testa individualmente o Servo Tilt (Cima/Baixo)
  Serial.println("[AUTOTESTE] Movendo Servo Tilt (Cima/Baixo) -> pino D23...");
  servoTilt.write(0);   // Vai para baixo total
  delay(800);
  servoTilt.write(180); // Vai para cima total
  delay(800);
  servoTilt.write(90);  // Volta ao centro
  delay(800);
  
  Serial.println("[AUTOTESTE] Concluido com sucesso!");
  Serial.println("ESP32 Solar Tracker Inicializado! Pinos: Pan=18, Tilt=23 (D23)");
}

void loop() {
  // Leitura Serial NÃO-BLOQUEANTE
  while (Serial.available() > 0) {
    char caractere = (char)Serial.read();
    
    // Se encontrar quebra de linha, finaliza o comando para processamento
    if (caractere == '\n') {
      comandoCompleto = true;
    } 
    // Ignora retornos de carro (\r) e adiciona os caracteres normais
    else if (caractere != '\r') {
      comandoBuffer += caractere;
    }
  }

  // Processa o comando recebido se estiver completo
  if (comandoCompleto) {
    comandoBuffer.trim(); // Limpa espaços extras
    
    // O comando esperado é no formato: "P:90,T:45"
    int indiceP = comandoBuffer.indexOf("P:");
    int indiceVirgula = comandoBuffer.indexOf(",");
    int indiceT = comandoBuffer.indexOf("T:");
    
    if (indiceP != -1 && indiceT != -1) {
      // Extrai os valores numéricos da string de forma segura
      int novoPan = comandoBuffer.substring(indiceP + 2, indiceVirgula).toInt();
      int novoTilt = comandoBuffer.substring(indiceT + 2).toInt();
      
      // Move os motores garantindo limites físicos seguros de 0 a 180 graus
      novoPan = constrain(novoPan, 0, 180);
      novoTilt = constrain(novoTilt, 0, 180);
      
      // Move o Pan primeiro se houve alteração
      if (novoPan != posPan) {
        posPan = novoPan;
        servoPan.write(posPan);
        Serial.print("Motores: Pan movido para ");
        Serial.println(posPan);
        delay(600); // Aguarda o motor Pan completar o movimento (reduz pico de corrente)
      }
      
      // Move o Tilt em seguida se houve alteração
      if (novoTilt != posTilt) {
        posTilt = novoTilt;
        servoTilt.write(posTilt);
        Serial.print("Motores: Tilt movido para ");
        Serial.println(posTilt);
        delay(600); // Aguarda o motor Tilt completar o movimento (reduz pico de corrente)
      }
    }
    
    // Limpa o buffer para o próximo comando
    comandoBuffer = "";
    comandoCompleto = false;
  }
}
