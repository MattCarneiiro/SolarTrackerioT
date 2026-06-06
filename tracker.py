import cv2
import serial
import time
import os
import csv
from datetime import datetime

# ==========================================
# CONFIGURAÇÕES E CONSTANTES DO SISTEMA
# ==========================================

PORTA_SERIAL = 'COM5' 
BAUD_RATE = 115200
INDICE_CAMERA = 0          # 0 para integrada (notebook), 1 ou mais para USB externa
DB_FILE = 'historico_tracker.csv'
INTERVALO_AUDITORIA = 10.0 # Tempo (segundos) entre as gravações de fotos e logs no CSV

# Configurações de Calibração dos Motores
MAX_PAN = 180              # Limite horizontal (0 a 180°)
MIN_TILT = 0               # Limite vertical mínimo
MAX_TILT = 90              # Limite vertical máximo (segurança mecânica)
ZONA_MORTA = 30            # Área de tolerância no centro da tela em pixels (evita tremedeira)
PASSO_RASTREIO = 1         # Graus que o motor move por frame para centralizar o alvo suavemente

# INVERSÃO DE EIXOS (Mude para True se o motor estiver fugindo da luz)
INVERTER_PAN = True 
INVERTER_TILT = True

# Configurações da Varredura Inicial (Startup)
SEARCH_GRID_ROWS = 5
SEARCH_GRID_COLS = 5
SEARCH_DELAY = 1.0         # Tempo para a câmera focar após mover na busca inicial
SERVO_STEP_LONGO = 3       # Passos em graus para movimentos longos (apenas no startup e encerramento)
SERVO_STEP_DELAY = 0.05    # Delay de segurança mecânica nos movimentos longos


# ==========================================
# INICIALIZAÇÃO DE COMPONENTES
# ==========================================

os.makedirs('capturas', exist_ok=True)

if not os.path.exists(DB_FILE):
    with open(DB_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';') 
        writer.writerow(['Data_Hora', 'Caminho_Imagem', 'Posicao_Pan', 'Posicao_Tilt'])

try:
    print(f"Conectando ao ESP32 na porta {PORTA_SERIAL}...")
    esp32 = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    time.sleep(2)  
    print("Conectado com sucesso!")
except Exception as e:
    print(f"Erro crítico ao conectar no ESP32: {e}")
    exit()

cap = cv2.VideoCapture(INDICE_CAMERA)
if not cap.isOpened():
    print(f"Erro crítico: Não foi possível abrir a câmera {INDICE_CAMERA}")
    exit()

# Variáveis globais de controle de estado
pan = 0
tilt = 0
ultimo_envio_tempo = 0


# ==========================================
# FUNÇÕES DE COMUNICAÇÃO E MOVIMENTAÇÃO
# ==========================================

def enviar_comando_serial(p, t):
    """Envia o comando de posição diretamente ao ESP32."""
    comando = f"P:{p},T:{t}\n"
    try:
        esp32.write(comando.encode('utf-8'))
        esp32.flush()
    except Exception as e:
        print(f"[ERRO SERIAL] Falha ao transmitir dados: {e}")


def ler_feedbacks_esp32():
    """Lê os logs enviados pelo ESP32 para liberar o buffer da porta serial."""
    try:
        while esp32.in_waiting > 0:
            linha = esp32.readline().decode('utf-8', errors='ignore').strip()
            if linha:
                print(f"[ESP32] {linha}")
    except Exception as e:
        pass


def mover_motores_gradualmente(dest_pan, dest_tilt):
    """Move os motores suavemente. Usado APENAS para saltos longos (Startup e Encerramento)."""
    global pan, tilt
    while pan != dest_pan or tilt != dest_tilt:
        if pan < dest_pan:
            pan = min(dest_pan, pan + SERVO_STEP_LONGO)
        elif pan > dest_pan:
            pan = max(dest_pan, pan - SERVO_STEP_LONGO)

        if tilt < dest_tilt:
            tilt = min(dest_tilt, tilt + SERVO_STEP_LONGO)
        elif tilt > dest_tilt:
            tilt = max(dest_tilt, tilt - SERVO_STEP_LONGO)

        enviar_comando_serial(pan, tilt)
        time.sleep(SERVO_STEP_DELAY)


# ==========================================
# FUNÇÕES DE IMAGEM E BANCO DE DADOS
# ==========================================

def tratar_frame(frame_bruto):
    """Rotaciona a imagem (câmera instalada de ponta-cabeça)."""
    return cv2.rotate(frame_bruto, cv2.ROTATE_180)


def calcular_intensidade_global(frame):
    """Retorna o nível máximo de brilho do frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    _, max_val, _, _ = cv2.minMaxLoc(blur)
    return max_val


def salvar_dados_e_imagem(frame, x, y, cx, cy, p, t):
    """Registra log no CSV e salva a foto com marcações na pasta capturas."""
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_hora_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_imagem = f"capturas/tracker_{data_hora_arquivo}.jpg"
    
    frame_auditoria = frame.copy()
    cv2.circle(frame_auditoria, (x, y), 20, (0, 255, 0), 2)
    cv2.circle(frame_auditoria, (cx, cy), ZONA_MORTA, (255, 0, 0), 1)
    cv2.putText(frame_auditoria, f"Data: {data_hora}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame_auditoria, f"Pan: {p}* | Tilt: {t}*", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    cv2.imwrite(caminho_imagem, frame_auditoria)
    
    try:
        with open(DB_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([data_hora, caminho_imagem, p, t])
    except Exception as e:
        print(f"[ERRO DB] Falha ao registrar no CSV: {e}")


def realizar_varredura_inicial():
    """Mapeia o céu em posições pré-definidas para encontrar o foco inicial do Sol."""
    global pan, tilt
    print("[STARTUP] Movendo para a posição inicial (0,0)...")
    mover_motores_gradualmente(0, 0)
    time.sleep(1)

    melhor_captura = {'valor': -1, 'pan': 0, 'tilt': 0}
    posicoes_busca = []
    
    for linha in range(SEARCH_GRID_ROWS):
        for coluna in range(SEARCH_GRID_COLS):
            p = int(round(linha * MAX_PAN / (SEARCH_GRID_ROWS - 1)))
            t = int(round(coluna * MAX_TILT / (SEARCH_GRID_COLS - 1)))
            posicoes_busca.append((p, t))

    print(f"[STARTUP] Iniciando varredura em {len(posicoes_busca)} pontos...")
    for idx, (p, t) in enumerate(posicoes_busca, start=1):
        mover_motores_gradualmente(p, t)
        time.sleep(SEARCH_DELAY)
        
        ret, frame_bruto = cap.read()
        if not ret: continue

        frame = tratar_frame(frame_bruto)
        valor_brilho = calcular_intensidade_global(frame)
        print(f" -> Checando Ponto {idx}: Pan={p}°, Tilt={t}° | Brilho: {valor_brilho:.1f}")
        
        if valor_brilho > melhor_captura['valor']:
            melhor_captura = {'valor': valor_brilho, 'pan': p, 'tilt': t}

    pan = melhor_captura['pan']
    tilt = melhor_captura['tilt']
    mover_motores_gradualmente(pan, tilt)
    print(f"[STARTUP] Alvo fixado! Iniciando rastreamento contínuo a partir de Pan:{pan}°, Tilt:{tilt}°\n")


# ==========================================
# LOOP PRINCIPAL DO SISTEMA (EXECUÇÃO)
# ==========================================

realizar_varredura_inicial()
print("Sistema operando em Malha Fechada (Step-and-Check). Pressione 'q' na tela de vídeo para sair.")

try:
    while True:
        ret, frame_bruto = cap.read()
        if not ret:
            break
        
        frame = tratar_frame(frame_bruto)
        altura, largura, _ = frame.shape
        centro_x, centro_y = largura // 2, altura // 2
        
        # =================================================================
        # 1. PROCESSAMENTO DA IMAGEM GERAL E CENTRÓIDE
        # =================================================================
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Filtra a imagem: isola a mancha de luz (brilho acima de 220 vira branco puro)
        _, mascara_luz = cv2.threshold(gray_blur, 220, 255, cv2.THRESH_BINARY)
        
        # Calcula os "Momentos" (centro de massa/geometria) dessa mancha branca
        momentos = cv2.moments(mascara_luz)
        
        if momentos["m00"] > 0:
            luz_x = int(momentos["m10"] / momentos["m00"])
            luz_y = int(momentos["m01"] / momentos["m00"])
        else:
            # Failsafe: se a luz estiver muito fraca, usa o método do pixel único
            _, _, _, max_loc = cv2.minMaxLoc(gray_blur)
            luz_x, luz_y = max_loc
            
        # ---> LINHAS CORRIGIDAS AQUI <---
        # Calcula a distância em pixels entre o centro da luz e o centro da câmera
        erro_x = luz_x - centro_x
        erro_y = luz_y - centro_y
        
        houve_movimento = False

        # 2. LÓGICA DE MOVIMENTO (STEP-AND-CHECK)
        if abs(erro_x) > ZONA_MORTA:
            direcao_pan = PASSO_RASTREIO if erro_x > 0 else -PASSO_RASTREIO
            if INVERTER_PAN:
                direcao_pan *= -1
            pan += direcao_pan
            houve_movimento = True

        if abs(erro_y) > ZONA_MORTA:
            direcao_tilt = PASSO_RASTREIO if erro_y > 0 else -PASSO_RASTREIO
            if INVERTER_TILT:
                direcao_tilt *= -1
            tilt += direcao_tilt
            houve_movimento = True

        # Restringe limites de segurança física
        pan = max(0, min(MAX_PAN, pan))
        tilt = max(MIN_TILT, min(MAX_TILT, tilt))

        # Dispara movimento físico
        if houve_movimento:
            enviar_comando_serial(pan, tilt)
            time.sleep(0.05) # Pausa mínima para o motor agir antes do próximo frame

        # 3. SALVAMENTO E LOGS (Executado apenas a cada 10 segundos)
        tempo_atual = time.time()
        if tempo_atual - ultimo_envio_tempo >= INTERVALO_AUDITORIA:
            ultimo_envio_tempo = tempo_atual
            print(f"[Auditoria] Posição atualizada -> Pan:{pan}°, Tilt:{tilt}° (Alvo em X:{luz_x} Y:{luz_y})")
            salvar_dados_e_imagem(frame, luz_x, luz_y, centro_x, centro_y, pan, tilt)

        # 4. INTERFACE E MANUTENÇÃO
        ler_feedbacks_esp32()
        
        cv2.circle(frame, (luz_x, luz_y), 20, (0, 255, 0), 2)           
        cv2.circle(frame, (centro_x, centro_y), ZONA_MORTA, (255, 0, 0), 1) 
        cv2.imshow('Solar Tracker - Controle de Visao', frame)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

finally:
    print("\n[ENCERRAMENTO] Retornando rastreador para a posição de segurança (0,0)...")
    mover_motores_gradualmente(0, 0)
    cap.release()
    cv2.destroyAllWindows()
    esp32.close()
    print("Sistema encerrado com segurança.")