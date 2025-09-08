import React, { useEffect, useState } from "react";
import "./Sensores.css";

function Sensores() {
  const [sensores, setSensores] = useState([]);
  const [medidas, setMedidas] = useState([]);
  const [nuevo, setNuevo] = useState({
    sensor: "",
    tipo_sensor: "",
    activo: true,
    campos: [{ nombre_campo: "", tipo_campo: "" }],
  });
  const [editando, setEditando] = useState(null);

  const opcionesTipoCampo = ["float", "number", "entero", "boolean"];

  const cargarSensores = () => {
    fetch("http://127.0.0.1:5000/listar_sensores_campos")
      .then((res) => res.json())
      .then((data) => setSensores(data))
      .catch((err) => console.error("Error cargando sensores:", err));
  };

  const cargarMedidas = () => {
    fetch("http://127.0.0.1:5000/medidas")
      .then((res) => res.json())
      .then((data) => setMedidas(data))
      .catch((err) => console.error("Error cargando medidas:", err));
  };

  useEffect(() => {
    cargarSensores();
    cargarMedidas();
    const intervalo = setInterval(cargarMedidas, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const agregarCampo = () => {
    setNuevo({
      ...nuevo,
      campos: [...nuevo.campos, { nombre_campo: "", tipo_campo: "" }],
    });
  };

  const agregarCampoEdicion = () => {
    setEditando({
      ...editando,
      campos: [...editando.campos, { nombre_campo: "", tipo_campo: "" }],
    });
  };

  const actualizarCampo = (index, key, value) => {
    const nuevosCampos = [...nuevo.campos];
    nuevosCampos[index][key] = value;
    setNuevo({ ...nuevo, campos: nuevosCampos });
  };

  const actualizarCampoEdicion = (index, key, value) => {
    const nuevosCampos = [...editando.campos];
    nuevosCampos[index][key] = value;
    setEditando({ ...editando, campos: nuevosCampos });
  };

  const eliminarCampo = (index) => {
    const nuevosCampos = nuevo.campos.filter((_, i) => i !== index);
    setNuevo({ ...nuevo, campos: nuevosCampos });
  };

  const eliminarCampoEdicion = (index) => {
    const nuevosCampos = editando.campos.filter((_, i) => i !== index);
    setEditando({ ...editando, campos: nuevosCampos });
  };

  const agregarSensor = () => {
    fetch("http://127.0.0.1:5000/agregar_sensor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(nuevo),
    })
      .then((res) => res.json())
      .then(() => {
        setNuevo({
          sensor: "",
          tipo_sensor: "",
          activo: true,
          campos: [{ nombre_campo: "", tipo_campo: "" }],
        });
        cargarSensores();
      })
      .catch((err) => console.error("Error agregando sensor:", err));
  };

  const guardarEdicion = () => {
    fetch(`http://127.0.0.1:5000/editar_sensor/${editando.sensor_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...editando,
        activo: Boolean(editando.activo),
      }),
    })
      .then((res) => res.json())
      .then(() => {
        setEditando(null);
        cargarSensores();
      })
      .catch((err) => console.error("Error editando sensor:", err));
  };

  const toggleEstadoSensor = async (sensor_id, sensor_activo, sensor_nombre) => {
    const nuevoEstado = !sensor_activo;
    const accion = nuevoEstado ? "encender" : "apagar";
    
    if (!window.confirm(`¿Seguro que deseas ${accion} el sensor "${sensor_nombre}"?`)) return;

    try {
      const res = await fetch(`http://127.0.0.1:5000/editar_sensor/${sensor_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          activo: nuevoEstado
        }),
      });

      if (!res.ok) throw new Error(`Error al ${accion} sensor`);

      const data = await res.json();
      alert(data.mensaje || `Sensor ${accion === 'encender' ? 'encendido' : 'apagado'} correctamente`);
      
      cargarSensores();
    } catch (err) {
      console.error(`Error al ${accion} sensor:`, err);
      alert(`No se pudo ${accion} el sensor. Revisa el backend.`);
    }
  };

  const eliminarSensorDefinitivamente = async (sensor_id, sensor_nombre) => {
    if (!window.confirm(`¿ESTÁS SEGURO? Esta acción eliminará permanentemente el sensor "${sensor_nombre}" y todas sus medidas. ¡Esta acción no se puede deshacer!`)) return;

    try {
      const res = await fetch(`http://127.0.0.1:5000/eliminar_sensor_definitivo/${sensor_id}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Error eliminando sensor definitivamente");

      const data = await res.json();
      alert(data.mensaje || "Sensor eliminado definitivamente");
      
      cargarSensores();
      cargarMedidas();
      
    } catch (err) {
      console.error("Error eliminando sensor:", err);
      alert("No se pudo eliminar el sensor definitivamente.");
    }
  };

  return (
    <div className="contenedor">
      <h2 className="titulo">➕ Agregar Sensor</h2>
      <div className="formulario">
        <input
          type="text"
          placeholder="Nombre Sensor"
          value={nuevo.sensor}
          onChange={(e) => setNuevo({ ...nuevo, sensor: e.target.value })}
        />
        <input
          type="text"
          placeholder="Tipo Sensor"
          value={nuevo.tipo_sensor}
          onChange={(e) => setNuevo({ ...nuevo, tipo_sensor: e.target.value })}
        />
        <select
          value={nuevo.activo ? "true" : "false"}
          onChange={(e) =>
            setNuevo({ ...nuevo, activo: e.target.value === "true" })
          }
        >
          <option value="true">Activo</option>
          <option value="false">Inactivo</option>
        </select>

        <h4>Campos</h4>
        {nuevo.campos.map((campo, i) => (
          <div key={i} className="campo-grupo">
            <input
              type="text"
              placeholder="Nombre Campo"
              value={campo.nombre_campo}
              onChange={(e) => actualizarCampo(i, "nombre_campo", e.target.value)}
            />
            <select
              value={campo.tipo_campo}
              onChange={(e) => actualizarCampo(i, "tipo_campo", e.target.value)}
            >
              <option value="">Selecciona tipo</option>
              {opcionesTipoCampo.map((tipo) => (
                <option key={tipo} value={tipo}>
                  {tipo}
                </option>
              ))}
            </select>
            {nuevo.campos.length > 1 && (
              <button
                className="btn-eliminar-campo"
                onClick={() => eliminarCampo(i)}
              >
                X
              </button>
            )}
          </div>
        ))}
        <button className="btn-agregar-campo" onClick={agregarCampo}>
          + Añadir Campo
        </button>

        <button className="btn-guardar" onClick={agregarSensor}>
          Guardar
        </button>
      </div>

      <h2 className="titulo">📋 Lista de Sensores</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Activo</th>
            <th>Campos</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sensores.map((s) => (
            <tr key={s.sensor_id}>
              <td>{s.sensor_id}</td>
              <td>{s.sensor}</td>
              <td>{s.tipo_sensor}</td>
              <td className={s.activo ? "activo" : "inactivo"}>
                {s.activo ? "Sí" : "No"}
              </td>
              <td>
                <ul>
                  {s.campos.map((c) => (
                    <li key={c.campo_id}>
                      {c.nombre_campo} ({c.tipo_campo})
                    </li>
                  ))}
                </ul>
              </td>
              <td>
                <button
                  className="btn-editar"
                  onClick={() => setEditando({...s})}
                >
                  Editar
                </button>
                <button
                  className={s.activo ? "btn-apagar" : "btn-encender"}
                  onClick={() => toggleEstadoSensor(s.sensor_id, s.activo, s.sensor)}
                  title={s.activo ? "Apagar sensor" : "Encender sensor"}
                >
                  {s.activo ? "🌙 Apagar" : "💡 Encender"}
                </button>
                <button
                  className="btn-eliminar-definitivo"
                  onClick={() => eliminarSensorDefinitivamente(s.sensor_id, s.sensor)}
                  title="Eliminar permanentemente"
                >
                  🗑️ Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {editando && (
        <div className="panel-edicion">
          <h3>✏️ Editar Sensor</h3>
          <input
            type="text"
            value={editando.sensor}
            onChange={(e) => setEditando({ ...editando, sensor: e.target.value })}
          />
          <input
            type="text"
            value={editando.tipo_sensor}
            onChange={(e) =>
              setEditando({ ...editando, tipo_sensor: e.target.value })
            }
          />
          <select
            value={editando.activo ? "true" : "false"}
            onChange={(e) =>
              setEditando({ ...editando, activo: e.target.value === "true" })
            }
          >
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
          </select>

          <h4>Campos</h4>
          {editando.campos.map((campo, i) => (
            <div key={i} className="campo-grupo">
              <input
                type="text"
                placeholder="Nombre Campo"
                value={campo.nombre_campo}
                onChange={(e) => actualizarCampoEdicion(i, "nombre_campo", e.target.value)}
              />
              <select
                value={campo.tipo_campo}
                onChange={(e) => actualizarCampoEdicion(i, "tipo_campo", e.target.value)}
              >
                <option value="">Selecciona tipo</option>
                {opcionesTipoCampo.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>
              {editando.campos.length > 1 && (
                <button
                  className="btn-eliminar-campo"
                  onClick={() => eliminarCampoEdicion(i)}
                >
                  X
                </button>
              )}
            </div>
          ))}
          
          <button className="btn-agregar-campo" onClick={agregarCampoEdicion}>
            + Añadir Campo
          </button>

          <button className="btn-guardar" onClick={guardarEdicion}>
            Guardar Cambios
          </button>
          <button className="btn-cancelar" onClick={() => setEditando(null)}>
            Cancelar
          </button>
        </div>
      )}

      <h2 className="titulo">📊 Últimas Medidas</h2>
      <table>
        <thead>
          <tr>
            <th>Sensor</th>
            <th>Campo</th>
            <th>Valor</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {medidas.length > 0 ? (
            medidas.map((m, i) => (
              <tr key={i}>
                <td>{m.sensor}</td>
                <td>{m.nombre_campo}</td>
                <td>{m.valor}</td>
                <td>{m.fecha}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="4">No hay medidas registradas</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Sensores;