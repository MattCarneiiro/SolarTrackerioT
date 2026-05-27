#!/bin/bash
# Script para iniciar o Solar Tracker Dashboard localmente
# Funciona em Linux/Mac

echo ""
echo "===================================================="
echo "  Solar Tracker Dashboard - Inicializador Local"
echo "===================================================="
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "[!] Ambiente virtual não encontrado!"
    echo "[*] Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Instala dependências (se houver)
echo "[*] Verificando dependências..."
pip install -q -r requirements.txt 2>/dev/null

# Inicia o servidor
echo ""
echo "[✓] Iniciando servidor..."
echo ""
python dashboard_server.py
