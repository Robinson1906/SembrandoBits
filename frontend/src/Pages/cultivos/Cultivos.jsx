import React from "react";
import "./cultivossytle.css";

function Servicios() {
  return (
    <div className="servicios-container">
      <div className="servicios-content">
        <h2 className="text-2xl font-bold mb-4">Nuestros Servicios ⚙️</h2>
        <ul className="list-disc pl-6 text-gray-700">
          <li>Monitoreo de sensores</li>
          <li>Control de riego inteligente</li>
          <li>Análisis de datos IoT</li>
        </ul>
      </div>

      <div className="servicios-aside">
      </div>
    </div>
  );
}

export default Servicios;
