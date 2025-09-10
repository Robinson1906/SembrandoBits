SembrandoBits - Despliegue Unificado Backend + Frontend
=======================================================

Objetivo: Servir el frontend (React + Vite) desde Flask para que cualquier dispositivo en la red (o vía IP pública) acceda a una sola URL y las peticiones API funcionen sin configurar IPs manualmente.

Pasos:
1. Instalar dependencias
   - Backend: pip install -r Backend/requirements.txt
   - Frontend: cd frontend && npm install

2. Construir frontend
   cd frontend
   npm run build
   (Esto genera carpeta dist/ con assets.)

3. Iniciar backend
   cd Backend
   python servidor.py

4. Acceder desde otro dispositivo
   - Usar IP LAN de la máquina: http://<IP_LAN>:8860/
   - La SPA y API comparten origen (same-origin), por lo tanto fetch usa window.location.origin.

Variables opcionales:
 - PORT: cambiar puerto del backend (default 8860)
 - BIND_HOST: host de escucha (default 0.0.0.0)

Verificación:
 - GET /health  (estado rápido)
 - GET /listar_sensores_campos (lista sensores)
 - GET /medidas?limite=10

Rebuild frontend tras cambios:
 - npm run build nuevamente; reiniciar backend o borrar cache navegador.

Problemas comunes:
 - No carga assets: asegurarse que dist/ existe y que index.html está en frontend/dist.
 - Failed to fetch desde móvil: firewall Windows bloqueando puerto 8860.
 - Acceso vía IP pública falla pero LAN funciona: configurar port forwarding en router.

Fin.