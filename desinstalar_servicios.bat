@echo off
echo Deteniendo y desinstalando servicios...

nssm\nssm-2.24\win64\nssm.exe stop SembrandoBitsBackend
nssm\nssm-2.24\win64\nssm.exe remove SembrandoBitsBackend confirm

nssm\nssm-2.24\win64\nssm.exe stop SembrandoBitsFrontend
nssm\nssm-2.24\win64\nssm.exe remove SembrandoBitsFrontend confirm

echo Servicios desinstalados.
