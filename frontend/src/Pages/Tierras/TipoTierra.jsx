import React, { useEffect, useState } from "react";
import "./tipotierrastyle.css";

function TipoTierra() {
  const [datos, setDatos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/sensores_db")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Error en la respuesta del servidor");
        }
        return res.json();
      })
      .then((data) => {
        console.log("Datos recibidos:", data);
        if (Array.isArray(data)) {
          setDatos(data);
        } else {
          console.error("La API no devolvió un array:", data);
          setDatos([]);
        }
      })
      .catch((err) => console.error("Error cargando datos:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="sensor-container">
      <h2 className="sensor-title">Datos del Sensor de Tierra 🌱</h2>

      {loading ? (
        <p className="loading-text">Cargando datos...</p>
      ) : datos.length > 0 ? (
        <div className="table-wrapper">
          <table className="sensor-table">
            <thead>
              <tr>
                {Object.keys(datos[0]).map((col, i) => (
                  <th key={i}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {datos.map((fila, i) => (
                <tr key={i}>
                  {Object.values(fila).map((valor, j) => (
                    <td key={j}>{valor}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="no-data">No se encontraron datos.</p>
      )}
    </div>
  );
}

export default TipoTierra;
