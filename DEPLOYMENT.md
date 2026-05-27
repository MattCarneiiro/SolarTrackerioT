

## ✅ Arquivos já criados/ajustados:

- ✅ `requirements.txt` - Dependências Python (seu projeto usa stdlib!)
- ✅ `Procfile` - Instrui Railway como executar o servidor
- ✅ `.gitignore` - Evita fazer upload de arquivos desnecessários
- ✅ `dashboard_server.py` - Ajustado para variáveis de ambiente

## 🔧 Como fazer o deploy em 5 minutos:

### 1️⃣ **Crie uma conta no Railway** (gratuito)
   - Acesse: https://railway.app
   - Faça login com GitHub ou Google

### 2️⃣ **Crie um novo projeto**
   - Clique em "Create New Project"
   - Selecione "Deploy from GitHub"
   - Selecione este repositório (`SolarTracker`)

### 3️⃣ **Configure as variáveis de ambiente** (se necessário)
   - Railway detectará automaticamente que é Python
   - A porta será configurada automaticamente via variável `PORT`
   - ✅ Pronto! Nada a configurar por padrão

### 4️⃣ **Deploy automático**
   - Railway fará build e deploy automaticamente
   - Você verá a URL gerada (algo como: `https://solartracker-production.up.railway.app`)

### 5️⃣ **Acessar o Dashboard**
   - Clique na URL do seu projeto no Railway
   - O dashboard estará disponível na raiz: `/`
   - API de dados disponível em: `/api/data`

---

## 📁 Estrutura esperada:

```
SolarTracker/
├── dashboard_server.py      ← Arquivo principal
├── dashboard.html           ← Interface web
├── requirements.txt         ← Dependências (criado)
├── Procfile                 ← Instruções de execução (criado)
├── .gitignore              ← Arquivos ignorados (criado)
├── historico_tracker.csv    ← Dados (subir manualmente ou via API)
└── capturas/               ← Imagens (se houver)
```

---

## 🔄 Sobre dados em tempo real (tracker.py):

O arquivo `tracker.py` **não pode ser executado na nuvem** porque depende de:
- Hardware específico (ESP32 via porta serial COM5)
- Webcam USB conectada

### Soluções:

**Opção 1: Dashboard lê dados estáticos** ✅ (Recomendado)
- Continue rodando `tracker.py` localmente
- Ele salva dados em `historico_tracker.csv`
- Faça upload do CSV para o Railway periodicamente
- Dashboard mostra histórico atualizado

**Opção 2: API centralizada** (Avançado)
- Modifique `tracker.py` para enviar dados via HTTP POST para um endpoint da nuvem
- Dashboard mostra dados em tempo real
- Requer mais configuração

---

## 📝 Próximas etapas opcionais:

1. **Banco de dados**: Se quiser dados persistentes na nuvem
   - Railway oferece PostgreSQL/MySQL grátis
   - Modifique `dashboard_server.py` para usar banco de dados

2. **Autenticação**: Se quiser proteger o dashboard
   - Adicione autenticação simples com variáveis de ambiente

3. **Domínio customizado**: 
   - Railway permite conectar domínios próprios

---

## ❓ Dúvidas?

- Railway docs: https://docs.railway.app
- Python on Railway: https://docs.railway.app/guides/python

**Seu projeto está pronto para o mundo! 🌍✨**
