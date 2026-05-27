# Documentação de Tecnologias

Este projeto `SolarTracker` combina software Python, uma interface web de monitoramento, firmware para ESP32 e deployment em nuvem. A seguir estão as tecnologias utilizadas em cada parte do sistema.

## 1. Python

- `Python 3` como linguagem principal do backend de controle e servidor.
- `tracker.py` utiliza:
  - `opencv-python` (`cv2`) para captura de vídeo, processamento de imagem e desenhos de marcação.
  - `pyserial` para comunicação serial com o microcontrolador ESP32.
  - `time`, `datetime` e `os` para controle de temporização, criação de arquivos e organização de diretórios.
  - `csv` para registro de histórico de rastreamento em `historico_tracker.csv`.

- `dashboard_server.py` utiliza apenas bibliotecas padrão do Python:
  - `http.server` e `socketserver` para servir o dashboard HTML localmente.
  - `json` para converter dados do CSV em JSON para consumo pela interface web.
  - `csv` para leitura do histórico gerado pelo `tracker.py`.
  - `os` para leitura de variáveis de ambiente e compatibilidade com diferentes plataformas.

## 2. Interface Web

- `dashboard.html` implementa o painel de visualização.
- Tecnologias usadas:
  - HTML5 para estrutura da página.
  - CSS moderno com `backdrop-filter`, gradientes e responsividade para layout visual atraente.
  - JavaScript puro para:
    - consumir a API `/api/data` fornecida pelo servidor Python,
    - renderizar gráficos dinâmicos,
    - atualizar KPIs e galeria de imagens automaticamente.
  - `ApexCharts` (via CDN) para gráficos interativos de área e scatter.
  - `FontAwesome` (via CDN) para ícones de interface.
  - `Google Fonts` (via CDN) com as fontes `Outfit` e `Inter`.

## 3. Firmware e Eletrônica

- `solar_tracker_esp32/solar_tracker_esp32.ino` é o firmware do microcontrolador.
- Tecnologias usadas:
  - `Arduino` / `ESP32` como plataforma embarcada.
  - `ESP32Servo` para controle de servomotores no ESP32.
  - Comunicação serial a `115200` bps entre o ESP32 e o script Python.
  - Controle de servos para dois eixos:
    - `pinServoPan = 18` para movimento horizontal (Pan).
    - `pinServoTilt = 23` para movimento vertical (Tilt).
  - Parser serial simples que espera mensagens no formato `P:<valor>,T:<valor>\n`.

## 4. Arquivos e Dados

- `historico_tracker.csv` grava o histórico de registros do rastreador.
  - Delimitador `;` usado para compatibilidade com Excel em português.
  - Campos gravados:
    - `Data_Hora`
    - `Caminho_Imagem`
    - `Posicao_Pan`
    - `Posicao_Tilt`
- Diretório `capturas/` armazena imagens geradas a cada ciclo de rastreamento.

## 5. Deployment e Produção

### Arquivos de Configuração

- `requirements.txt`: Lista de dependências Python (atualmente vazio pois o dashboard usa apenas stdlib).
- `Procfile`: Arquivo de configuração para Railway que especifica como executar a aplicação.
- `.gitignore`: Evita fazer upload de arquivos desnecessários (venv, __pycache__, dados locais).
- `start_dashboard.bat`: Script batch para iniciar o servidor no Windows.
- `start_dashboard.sh`: Script shell para iniciar o servidor no Linux/Mac.

### Deployment no Railway

- **Plataforma**: Railway (https://railway.app) - hosting gratuito para aplicações Python.
- **Variáveis de Ambiente**:
  - `PORT`: Porta HTTP dinamicamente atribuída pelo Railway (substitui hardcoded `8080`).
  - Servidor escuta em `0.0.0.0` para aceitar requisições externas.
- **Fluxo de Deploy**:
  - Conectar repositório GitHub ao Railway.
  - Railway detecta `Procfile` e `requirements.txt`.
  - Build automático com Python runtime.
  - Aplicação disponível em URL pública gerada.

## 6. Funcionamento Geral

### Execução Local

- Execute `start_dashboard.bat` (Windows) ou `./start_dashboard.sh` (Linux/Mac).
- Acesse http://localhost:8080 no navegador.
- O servidor serve `dashboard.html` na raiz (`/`) e API de dados em (`/api/data`).

### Fluxo de Dados

1. **Coleta** (`tracker.py` - local):
   - Captura frames da câmera.
   - Identifica o ponto de maior brilho (algoritmo de rastreamento solar).
   - Calcula ajustes de `pan` e `tilt`.
   - Envia comandos ao ESP32 via serial.
   - Salva foto de auditoria e registra dados em `historico_tracker.csv`.

2. **Exposição** (`dashboard_server.py`):
   - Serve interface web (`dashboard.html`).
   - Disponibiliza dados via API REST (`/api/data`).
   - Suporta execução local ou na nuvem.

3. **Visualização** (`dashboard.html`):
   - Consome API de dados.
   - Renderiza gráficos dinâmicos com ApexCharts.
   - Exibe KPIs e galeria de imagens.
   - Funciona em desktop e mobile.

## 7. Observações

- O sistema é **híbrido**: `tracker.py` executa localmente (dependências de hardware), enquanto `dashboard_server.py` pode rodar na nuvem.
- **Dados**: Historicamente armazenados em CSV local, podendo ser sincronizados com banco de dados na nuvem (PostgreSQL, MySQL) para melhor escalabilidade.
- **Interface**: Usa tecnologias web modernas (HTML5, CSS3, JavaScript puro) com bibliotecas externas via CDN (ApexCharts, FontAwesome, Google Fonts).
- **Firmware**: Arduino/ESP32 com comunicação serial bidirecional (recebe comandos, envia telemetria).
