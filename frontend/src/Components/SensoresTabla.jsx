import { useEffect, useState } from "react";

function SensorTable() {
  const [datos, setDatos] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/sensores_db")
      .then((res) => res.json())
      .then((data) => setDatos(data))
      .catch((err) => console.error("Error cargando datos:", err));
  }, []);

  return (
    <div className="overflow-x-auto mt-6">
      <table className="table-auto w-full border-collapse border border-gray-200">
        <thead>
          <tr className="bg-blue-600 text-white">
            <th className="border px-4 py-2">ID</th>
            <th className="border px-4 py-2">Fecha</th>
            <th className="border px-4 py-2">Dispositivo</th>
            <th className="border px-4 py-2">Tipo de Sensor</th>
            <th className="border px-4 py-2">Valor</th>
          </tr>
        </thead>
        <tbody>
          {datos.map((item) => (
            <tr key={item.id} className="hover:bg-gray-100">
              <td className="border px-4 py-2">{item.id}</td>
              <td className="border px-4 py-2">{item.fecha}</td>
              <td className="border px-4 py-2">{item.dispositivo}</td>
              <td className="border px-4 py-2">{item.tipo_sensor}</td>
              <td className="border px-4 py-2">{item.valor}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SensorTable;
