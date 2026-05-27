# ☀️ Solar Tracker - Dashboard em Nuvem

Dashboard web interativo para monitoramento em tempo real de um rastreador solar automático alimentado por ESP32.

## 🎯 Características

- **Dashboard web responsivo** - Interface intuitiva com gráficos de movimento solar
- **Histórico de dados** - Registro CSV de todas as movimentações
- **Galeria de fotos** - Visualização de capturas da câmera integrada
- **Deploy gratuito** - Hospedado na nuvem com Railway

## 🚀 Quick Start - Deploy em Nuvem (Railway)

### ⚡ 3 passos para colocar online:

1. **Crie conta no Railway** → https://railway.app (gratuito, sem cartão)
2. **Conecte seu GitHub** → Deploy this repository
3. **Pronto!** → URL gerada automaticamente

Veja [DEPLOYMENT.md](DEPLOYMENT.md) para instruções detalhadas.

---

## 🏠 Execução Local

### Windows:
```bash
start_dashboard.bat
```

### Linux/Mac:
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

Depois acesse: http://localhost:8080

---

## 📋 Estrutura do Projeto

```
SolarTracker/
│
├── dashboard_server.py          Servidor web (porta configurável)
├── dashboard.html               Interface web interativa
├── tracker.py                   Script de captura (ESP32 + câmera)
├── solar_tracker_esp32/
│   └── solar_tracker_esp32.ino  Firmware do ESP32
│
├── historico_tracker.csv        Dados persistentes
├── capturas/                    Fotos capturadas
│
├── requirements.txt             Dependências Python
├── Procfile                     Config para Railway
├── DEPLOYMENT.md                Guia de deployment
└── Documentation.md             Documentação técnica
```

---

## 🔌 Hardware Necessário

- **Microcontrolador**: ESP32
- **Motores**: 2x Servo (Pan-Tilt)
- **Câmera**: USB Webcam
- **Sensor Solar**: LDR ou similar

---

## 📊 API Endpoints

| Rota | Descrição |
|------|-----------|
| `/` | Dashboard principal |
| `/api/data` | JSON com histórico de dados |
| `/capturas/*` | Acesso às imagens capturadas |

**Exemplo de resposta `/api/data`:**
```json
[
  {
    "Data_Hora": "2024-05-27 14:30:00",
    "Caminho_Imagem": "capturas/solar_2024_05_27_14_30.jpg",
    "Posicao_Pan": 95,
    "Posicao_Tilt": 85,
    "is_mock": false
  }
]
```

---

## 🔄 Fluxo de Dados

```
ESP32 (Serial COM5)
    ↓
tracker.py (Coleta dados + fotos)
    ↓
historico_tracker.csv (Persistência local)
    ↓
dashboard_server.py (API HTTP)
    ↓
dashboard.html (Visualização)
```

---

## 🌐 Deployment - Próximas Etapas

- [x] Servidor configurado para Railway
- [ ] Banco de dados na nuvem (PostgreSQL)
- [ ] Sincronização automática de dados
- [ ] Autenticação de usuários
- [ ] Aplicativo mobile

---

## 📚 Documentação Adicional

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guia completo de deployment
- [Documentation.md](Documentation.md) - Detalhes técnicos
- [Railway Docs](https://docs.railway.app)

---

## 💬 Desenvolvedor - MattCarneiiro

Solar Tracker - Projeto educacional de rastreamento solar automático.

**Status**: ✅ Pronto para produção

---

**Dúvidas?** Confira [DEPLOYMENT.md](DEPLOYMENT.md) para troubleshooting.
