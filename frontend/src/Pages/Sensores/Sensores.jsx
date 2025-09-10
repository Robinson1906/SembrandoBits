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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const opcionesTipoCampo = ["float", "number", "int", "boolean", "string"];
  const API_BASE_URL = "http://localhost:5000";

  const cargarSensores = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/listar_sensores_campos`);
      if (!res.ok) throw new Error("Error al cargar sensores");
      const data = await res.json();
      setSensores(data);
    } catch (err) {
      console.error("Error cargando sensores:", err);
      setError("No se pudieron cargar los sensores");
    } finally {
      setLoading(false);
    }
  };

  const cargarMedidas = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/medidas?limite=20`);
      if (!res.ok) throw new Error("Error al cargar medidas");
      const data = await res.json();
      setMedidas(data);
    } catch (err) {
      console.error("Error cargando medidas:", err);
    }
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

  const agregarSensor = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/agregar_sensor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nuevo),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Error al agregar sensor");
      }

      const data = await res.json();
      alert(data.mensaje || "Sensor agregado correctamente");

      setNuevo({
        sensor: "",
        tipo_sensor: "",
        activo: true,
        campos: [{ nombre_campo: "", tipo_campo: "" }],
      });
      cargarSensores();
    } catch (err) {
      console.error("Error agregando sensor:", err);
      alert(err.message || "Error al agregar sensor");
    } finally {
      setLoading(false);
    }
  };

  const guardarEdicion = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/editar_sensor/${editando.sensor_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editando),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Error al editar sensor");
      }

      const data = await res.json();
      alert(data.mensaje || "Sensor actualizado correctamente");

      setEditando(null);
      cargarSensores();
    } catch (err) {
      console.error("Error editando sensor:", err);
      alert(err.message || "Error al editar sensor");
    } finally {
      setLoading(false);
    }
  };

  const toggleEstadoSensor = async (sensor_id, sensor_activo, sensor_nombre) => {
    const nuevoEstado = !sensor_activo;
    const accion = nuevoEstado ? "activar" : "desactivar";
    
    if (!window.confirm(`¿Seguro que deseas ${accion} el sensor "${sensor_nombre}"?`)) return;

    try {
      const res = await fetch(`${API_BASE_URL}/editar_sensor/${sensor_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ activo: nuevoEstado }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || `Error al ${accion} sensor`);
      }

      const data = await res.json();
      alert(data.mensaje || `Sensor ${accion}do correctamente`);
      
      cargarSensores();
    } catch (err) {
      console.error(`Error al ${accion} sensor:`, err);
      alert(err.message || `No se pudo ${accion} el sensor`);
    }
  };

  const eliminarSensorDefinitivamente = async (sensor_id, sensor_nombre) => {
    if (!window.confirm(`¿ESTÁS SEGURO? Esta acción eliminará permanentemente el sensor "${sensor_nombre}" y todas sus medidas. ¡Esta acción no se puede deshacer!`)) return;

    try {
      const res = await fetch(`${API_BASE_URL}/eliminar_sensor_definitivo/${sensor_id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Error eliminando sensor");
      }

      const data = await res.json();
      alert(data.mensaje || "Sensor eliminado definitivamente");
      
      cargarSensores();
      cargarMedidas();
    } catch (err) {
      console.error("Error eliminando sensor:", err);
      alert(err.message || "No se pudo eliminar el sensor");
    }
  };

  const formatearFecha = (timestamp) => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleString("es-ES");
  };

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <div className="contenedor">
      {error && <div className="error">{error}</div>}

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
          value={nuevo.activo}
          onChange={(e) => setNuevo({ ...nuevo, activo: e.target.value === "true" })}
        >
          <option value={true}>Activo</option>
          <option value={false}>Inactivo</option>
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

        <button className="btn-guardar" onClick={agregarSensor} disabled={loading}>
          {loading ? "Guardando..." : "Guardar Sensor"}
        </button>
      </div>

      <h2 className="titulo">📋 Lista de Sensores ({sensores.length})</h2>
      <div className="tabla-contenedor">
        <table className="tabla-sensores">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Campos</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {sensores.length === 0 ? (
              <tr>
                <td colSpan="5" className="no-data">No hay sensores registrados</td>
              </tr>
            ) : (
              sensores.map((s) => (
                <tr key={s.sensor_id} className={s.activo ? "activo" : "inactivo"}>
                  <td>{s.sensor}</td>
                  <td>{s.tipo_sensor}</td>
                  <td>
                    <span className={`estado ${s.activo ? "activo" : "inactivo"}`}>
                      {s.activo ? "🟢 Activo" : "🔴 Inactivo"}
                    </span>
                  </td>
                  <td>
                    <ul className="lista-campos">
                      {s.campos && s.campos.map((c) => (
                        <li key={c.campo_id}>
                          <strong>{c.nombre_campo}</strong> ({c.tipo_campo})
                          {c.activo === false && " ❌"}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td>
                    <div className="acciones">
                      <button
                        className="btn-editar"
                        onClick={() => setEditando({...s})}
                        title="Editar sensor"
                      >
                        ✏️
                      </button>
                      <button
                        className={s.activo ? "btn-desactivar" : "btn-activar"}
                        onClick={() => toggleEstadoSensor(s.sensor_id, s.activo, s.sensor)}
                        title={s.activo ? "Desactivar sensor" : "Activar sensor"}
                      >
                        {s.activo ? "⏸️" : "▶️"}
                      </button>
                      <button
                        className="btn-eliminar"
                        onClick={() => eliminarSensorDefinitivamente(s.sensor_id, s.sensor)}
                        title="Eliminar permanentemente"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {editando && (
        <div className="modal">
          <div className="modal-contenido">
            <h3>✏️ Editar Sensor</h3>
            <input
              type="text"
              placeholder="Nombre del sensor"
              value={editando.sensor}
              onChange={(e) => setEditando({ ...editando, sensor: e.target.value })}
            />
            <input
              type="text"
              placeholder="Tipo de sensor"
              value={editando.tipo_sensor}
              onChange={(e) => setEditando({ ...editando, tipo_sensor: e.target.value })}
            />
            <select
              value={editando.activo}
              onChange={(e) => setEditando({ ...editando, activo: e.target.value === "true" })}
            >
              <option value={true}>Activo</option>
              <option value={false}>Inactivo</option>
            </select>

            <h4>Campos</h4>
            {editando.campos && editando.campos.map((campo, i) => (
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

            <div className="modal-acciones">
              <button className="btn-guardar" onClick={guardarEdicion} disabled={loading}>
                {loading ? "Guardando..." : "Guardar Cambios"}
              </button>
              <button className="btn-cancelar" onClick={() => setEditando(null)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <h2 className="titulo">📊 Últimas Medidas ({medidas.length})</h2>
      <div className="tabla-contenedor">
        <table className="tabla-medidas">
          <thead>
            <tr>
              <th>Sensor</th>
              <th>Campo</th>
              <th>Valor</th>
              <th>Fecha/Hora</th>
            </tr>
          </thead>
          <tbody>
            {medidas.length === 0 ? (
              <tr>
                <td colSpan="4" className="no-data">No hay medidas registradas</td>
              </tr>
            ) : (
              medidas.map((m, i) => (
                <tr key={i}>
                  <td>{m.sensor}</td>
                  <td>{m.nombre_campo}</td>
                  <td className="valor">{m.valor}</td>
                  <td>{formatearFecha(m.timestamp)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Sensores;