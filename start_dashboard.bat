@echo off
REM Script para iniciar o Solar Tracker Dashboard localmente
REM Ativa o ambiente virtual e executa o servidor

echo.
echo ====================================================
echo  Solar Tracker Dashboard - Inicializador Local
echo ====================================================
echo.

REM Verifica se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo [!] Ambiente virtual nao encontrado!
    echo [*] Criando ambiente virtual...
    python -m venv venv
)

REM Ativa o ambiente virtual
call venv\Scripts\activate.bat

REM Instala dependências (se houver)
echo [*] Verificando dependências...
pip install -q -r requirements.txt 2>nul

REM Inicia o servidor
echo.
echo [✓] Iniciando servidor...
echo.
python dashboard_server.py

pause
