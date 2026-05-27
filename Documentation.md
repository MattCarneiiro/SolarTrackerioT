# Documentação de Tecnologias

Este projeto `SolarTracker` combina software Python, uma interface web de monitoramento e firmware para ESP32. A seguir estão as tecnologias utilizadas em cada parte do sistema.

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
  - `webbrowser` para abrir automaticamente o dashboard no navegador padrão.

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

## 5. Funcionamento geral

- O `tracker.py` captura frames da câmera, identifica o ponto de maior brilho e calcula ajustes de `pan` e `tilt`.
- A cada 10 segundos, ele envia comandos ao ESP32, salva uma foto de auditoria e registra os dados no CSV.
- O `dashboard_server.py` serve o `dashboard.html` e a API de dados para visualização em tempo real.
- A interface web consome os dados do CSV e apresenta gráficos, indicadores e galeria de imagens.

## 6. Observações

- O sistema se apoia em componentes de software locais (`Python`, `OpenCV`, `pyserial`) e em recursos web externos (`ApexCharts`, `FontAwesome`, `Google Fonts`).
- A base do firmware é Arduino/ESP32, enquanto o dashboard usa tecnologias web modernas para criar uma interface interativa.
