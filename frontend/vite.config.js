import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(() => {
  const port = Number(process.env.PORT || 5173);
  return {
    plugins: [react()],
    server: {
      host: true,          // Permite acceso desde otra máquina en la red
      port,                // Puedes cambiarlo exportando PORT=XXXX
      open: false,
      cors: true,
    }
  };
});
