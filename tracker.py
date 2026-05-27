import cv2
import serial
import time
import os
import csv
from datetime import datetime

#Configurações da porta serial para comunicação com o ESP32
PORTA_SERIAL = 'COM5' 
BAUD_RATE = 115200

# Criar a pasta de capturas de imagem se não existir
os.makedirs('capturas', exist_ok=True)

# Nome do arquivo do banco de dados (CSV otimizado para o Microsoft Excel)
DB_FILE = 'historico_tracker.csv'

# Cria o cabeçalho do CSV se o arquivo não existir
if not os.path.exists(DB_FILE):
    with open(DB_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';') # Delimitador ';' abre diretamente em colunas no Excel brasileiro
        writer.writerow(['Data_Hora', 'Caminho_Imagem', 'Posicao_Pan', 'Posicao_Tilt'])

try:
    print(f"Conectando ao ESP32 na porta {PORTA_SERIAL}...")
    esp32 = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    time.sleep(2) # Aguarda o ESP32 reiniciar após a conexão serial
    print("Conectado com sucesso!")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit()

# ÍNDICE DA CÂMERA:
# Geralmente: 0 = Câmera integrada (notebook), 1 ou 2 = Webcam externa USB.
# Definido como 1 por padrão para utilizar a webcam USB externa.
INDICE_CAMERA = 1

# Inicializa a Câmera
cap = cv2.VideoCapture(INDICE_CAMERA)

pan = 90
tilt = 90
zona_morta = 30

# Armazena os últimos valores enviados para evitar redundância na transmissão serial
pan_ultimo = -1
tilt_ultimo = -1

# Variáveis para controle de taxa de atualização (envio a cada 10 segundos)
ultimo_envio_tempo = 0
INTERVALO_ENVIO = 10.0  # segundos

# Guarda a última localização conhecida da fonte de luz para renderização contínua na janela OpenCV
luz_x = 0
luz_y = 0

print("Iniciando rastreamento... Pressione 'q' na janela do vídeo para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar imagem da câmera.")
        break
        
    altura, largura, _ = frame.shape
    centro_x, centro_y = largura // 2, altura // 2
    
    # Inicializa luz_x/y no centro da tela na primeira iteração
    if luz_x == 0 and luz_y == 0:
        luz_x, luz_y = centro_x, centro_y

    tempo_atual = time.time()
    
    # Executa a lógica de controle, captura de foto e gravação a cada 10 segundos
    if tempo_atual - ultimo_envio_tempo >= INTERVALO_ENVIO:
        ultimo_envio_tempo = tempo_atual
        
        # Converte para tons de cinza e aplica desfoque para focar na maior fonte de luz
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Acha o pixel mais claro
        _, _, _, max_loc = cv2.minMaxLoc(gray_blur)
        luz_x, luz_y = max_loc
        
        erro_x = luz_x - centro_x
        erro_y = luz_y - centro_y
        
        movimento = False
        
        # Lógica de Controle Proporcional Inteligente (para ciclos longos de 10s)
        if abs(erro_x) > zona_morta:
            # Mapeia proporcionalmente o erro de pixel para um ajuste de ângulo (máx 20 graus)
            ajuste_x = int((erro_x / (largura / 2)) * 20)
            if ajuste_x == 0:
                ajuste_x = 1 if erro_x > 0 else -1
                
            # NOTA: O sinal (-=) ajusta a direção do rastreamento. Inverta se o motor for ao contrário.
            pan -= ajuste_x
            movimento = True
            
        if abs(erro_y) > zona_morta:
            # Mapeia proporcionalmente o erro de pixel para um ajuste de ângulo (máx 20 graus)
            ajuste_y = int((erro_y / (altura / 2)) * 20)
            if ajuste_y == 0:
                ajuste_y = 1 if erro_y > 0 else -1
            tilt -= ajuste_y
            movimento = True
            
        pan = max(0, min(180, pan))
        tilt = max(0, min(180, tilt))
        
        # Envia para o ESP32 apenas se houver movimento e a posição mudou
        if movimento and (pan != pan_ultimo or tilt != tilt_ultimo):
            pan_ultimo = pan
            tilt_ultimo = tilt
            comando = f"P:{pan},T:{tilt}\n"
            try:
                esp32.write(comando.encode('utf-8'))
                esp32.flush()
                print(f"[PYTHON LOG] Enviando comando: P:{pan}, T:{tilt} (Luz em X:{luz_x}, Y:{luz_y})")
            except Exception as e:
                print(f"[PYTHON ERROR] Erro ao enviar para serial: {e}")
        else:
            print(f"[PYTHON LOG] Motores mantidos nas posições atuais: P:{pan}, T:{tilt}")
            
        # --- REGISTRO DE FOTO E HISTÓRICO NO BANCO DE DADOS (CSV) ---
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_hora_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_imagem = f"capturas/tracker_{data_hora_arquivo}.jpg"
        
        # Desenha marcações visuais na imagem a ser salva para auditoria
        frame_salvar = frame.copy()
        cv2.circle(frame_salvar, (luz_x, luz_y), 20, (0, 255, 0), 2)
        cv2.circle(frame_salvar, (centro_x, centro_y), zona_morta, (255, 0, 0), 1)
        # Carimba a data, hora e posições dos motores
        cv2.putText(frame_salvar, f"Data/Hora: {data_hora}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame_salvar, f"Pan (X): {pan} | Tilt (Y): {tilt}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Salva o arquivo de imagem no disco
        cv2.imwrite(caminho_imagem, frame_salvar)
        
        # Grava os dados na linha do CSV
        try:
            with open(DB_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([data_hora, caminho_imagem, pan, tilt])
            print(f"[BANCO DE DADOS] Registro salvo: {caminho_imagem} | Pan:{pan} | Tilt:{tilt}")
        except Exception as e:
            print(f"[PYTHON ERROR] Erro ao salvar no banco de dados: {e}")
    
    # Verifica e imprime feedback/logs vindos do ESP32 (fazemos isso continuamente para evitar travamento do buffer)
    try:
        while esp32.in_waiting > 0:
            linha_retorno = esp32.readline().decode('utf-8', errors='ignore').strip()
            if linha_retorno:
                print(f"[ESP32 Feedback] {linha_retorno}")
    except Exception as e:
        print(f"[PYTHON ERROR] Erro ao ler da serial: {e}")
    
    # Mostra a imagem na tela com marcações (desenho em tempo real baseado no último alvo calculado)
    cv2.circle(frame, (luz_x, luz_y), 20, (0, 255, 0), 2)
    cv2.circle(frame, (centro_x, centro_y), zona_morta, (255, 0, 0), 1)
    cv2.imshow('Solar Tracker', frame)
    
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp32.close()
print("Sistema encerrado.")