@echo off
echo Instalando servicios con NSSM...

REM Instalar servicio Backend
nssm\nssm-2.24\win64\nssm.exe install SembrandoBitsBackend "python.exe" "servidor.py"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsBackend AppDirectory "C:\Users\Smartcenter\Documents\GitHub\SembrandoBits\Backend"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsBackend DisplayName "SembrandoBits Backend"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsBackend Description "Servicio backend de SembrandoBits"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsBackend Start SERVICE_AUTO_START
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsBackend AppRestartDelay 5000

REM Instalar servicio Frontend
nssm\nssm-2.24\win64\nssm.exe install SembrandoBitsFrontend "npm.cmd" "run dev"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsFrontend AppDirectory "C:\Users\Smartcenter\Documents\GitHub\SembrandoBits\frontend"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsFrontend DisplayName "SembrandoBits Frontend"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsFrontend Description "Servicio frontend de SembrandoBits"
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsFrontend Start SERVICE_AUTO_START
nssm\nssm-2.24\win64\nssm.exe set SembrandoBitsFrontend AppRestartDelay 5000

echo Servicios instalados. Iniciando...
nssm\nssm-2.24\win64\nssm.exe start SembrandoBitsBackend
nssm\nssm-2.24\win64\nssm.exe start SembrandoBitsFrontend

echo Listo.
