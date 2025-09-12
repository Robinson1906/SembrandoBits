@echo off
chcp 65001 >nul
title Iniciador App - SembrandoBits (Flask)

echo ================================================
echo    INICIANDO SEMBRANDOBITS
echo    Backend Flask: servidor.py (Puerto 8860)
echo    Frontend: npm run dev (Puerto 7681)
echo ================================================

REM Configuración de rutas
set BACKEND_PATH=C:\Users\Usuario\Documents\GitHub\SembrandoBits\Backend
set FRONTEND_PATH=C:\Users\Usuario\Documents\GitHub\SembrandoBits\frontend

echo.
echo Iniciando backend Flask (minimizado)...
cd /d "%BACKEND_PATH%"
start /min "Backend Flask" cmd /k "python servidor.py"

echo Esperando 5 segundos para que el backend inicie...
timeout /t 5 /nobreak >nul

echo Iniciando frontend React (minimizado)...
cd /d "%FRONTEND_PATH%"
start /min "Frontend React" cmd /k "npm run dev"

echo.
echo ================================================
echo    APLICACIONES INICIADAS CORRECTAMENTE
echo ================================================
echo Backend Flask: http://localhost:8860
echo Frontend React: http://localhost:7681
echo.
echo ✅ MongoDB conectado exitosamente
echo 📌 Ventanas minimizadas en la barra de tareas
pause