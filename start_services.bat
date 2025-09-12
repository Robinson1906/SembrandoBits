@echo off
echo Starting SembrandoBits services...

REM Start Backend
cd /d "c:\Users\Smartcenter\Documents\GitHub\SembrandoBits\Backend"
start "Backend" python servidor.py

REM Start Frontend
cd /d "c:\Users\Smartcenter\Documents\GitHub\SembrandoBits\frontend"
start "Frontend" npm run dev

echo Services started.
