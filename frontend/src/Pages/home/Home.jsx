import React, { useState } from "react";
import "./stylehome.css";

function Home() {
  const [selectedCrop, setSelectedCrop] = useState("papa");
  const [frequency, setFrequency] = useState("AM");
  const [activeTab, setActiveTab] = useState("suelo");

  const amCrops = [
    { id: 'papa', name: 'Papa', icon: '🥔', frequency: "540" },
    { id: 'yuca', name: 'Yuca', icon: '🌿', frequency: "800" },
    { id: 'maiz', name: 'Maíz', icon: '🌽', frequency: "1100" }
  ];

  const fmCrops = [
    { id: 'frijol', name: 'Frijol', icon: '🥘', frequency: "88.5" },
    { id: 'tomate', name: 'Tomate', icon: '🍅', frequency: "102.3" },
    { id: 'zanahoria', name: 'Zanahoria', icon: '🥕', frequency: "107.7" }
  ];

  const sensorData = {
    papa: [
      { type: 'Temperatura', value: '22°C', status: 'ideal', description: 'Perfecta para el crecimiento' },
      { type: 'Humedad', value: '60%', status: 'buena', description: 'Buena para el desarrollo' },
      { type: 'PH', value: '6.2', status: 'optimo', description: 'Nivel adecuado' },
      { type: 'Nutrientes', value: 'Alto', status: 'buena', description: 'Suelo rico en nutrientes' }
    ],
    yuca: [
      { type: 'Temperatura', value: '25°C', status: 'ideal', description: 'Ideal para yuca' },
      { type: 'Humedad', value: '55%', status: 'regular', description: 'Podría mejorar con riego' },
      { type: 'PH', value: '5.8', status: 'optimo', description: 'Adecuado para yuca' },
      { type: 'Drenaje', value: 'Bueno', status: 'buena', description: 'Buen drenaje del suelo' }
    ],
    maiz: [
      { type: 'Temperatura', value: '24°C', status: 'ideal', description: 'Perfecta para maíz' },
      { type: 'Humedad', value: '65%', status: 'buena', description: 'Condición favorable' },
      { type: 'PH', value: '6.5', status: 'optimo', description: 'PH adecuado' },
      { type: 'Luz', value: '85%', status: 'ideal', description: 'Ideal para crecimiento' }
    ],
    frijol: [
      { type: 'Temperatura', value: '23°C', status: 'ideal', description: 'Ideal para frijol' },
      { type: 'Humedad', value: '50%', status: 'regular', description: 'Necesita más riego' },
      { type: 'PH', value: '6.0', status: 'optimo', description: 'Nivel perfecto' },
      { type: 'Nitrógeno', value: 'Optimo', status: 'buena', description: 'Buen nivel de nitrógeno' }
    ],
    tomate: [
      { type: 'Temperatura', value: '26°C', status: 'ideal', description: 'Perfecta para tomate' },
      { type: 'Humedad', value: '70%', status: 'buena', description: 'Condición favorable' },
      { type: 'PH', value: '6.3', status: 'optimo', description: 'PH adecuado' },
      { type: 'Luz', value: '90%', status: 'ideal', description: 'Ideal para tomate' }
    ],
    zanahoria: [
      { type: 'Temperatura', value: '20°C', status: 'ideal', description: 'Perfecta para zanahoria' },
      { type: 'Humedad', value: '60%', status: 'buena', description: 'Condición favorable' },
      { type: 'PH', value: '6.8', status: 'optimo', description: 'PH adecuado' },
      { type: 'Suelo', value: 'Arenoso', status: 'ideal', description: 'Ideal para zanahoria' }
    ]
  };

  const landSuitability = {
    papa: {
      status: 'apta',
      description: '✅ Tu tierra es PERFECTA para cultivar papa. Las condiciones son excelentes para un buen crecimiento.',
      recommendations: [
        'Mantén la humedad entre 55-65%',
        'Controla las plagas con métodos naturales',
        'Riega temprano en la mañana',
        'Añade abono orgánico cada 3 semanas',
        'Rotación de cultivos: espera 3 años antes de volver a plantar papa en la misma zona'
      ],
      planting: 'Época ideal: Febrero - Marzo',
      harvest: 'Cosecha en: 3-4 meses',
      tips: 'Evita el exceso de agua para prevenir hongos'
    },
    yuca: {
      status: 'moderadamente-apta',
      description: '⚠️ Tu tierra puede servir para yuca, pero necesita algunos ajustes para mejores resultados.',
      recommendations: [
        'Aumenta el riego ligeramente',
        'Considera añadir abono orgánico',
        'Protege del exceso de sol con malla sombra',
        'Mejora el drenaje del suelo',
        'Controla malezas regularmente'
      ],
      planting: 'Época ideal: Abril - Mayo',
      harvest: 'Cosecha en: 8-12 meses',
      tips: 'Prefiere suelos bien drenados'
    },
    maiz: {
      status: 'apta',
      description: '✅ Tu tierra es IDEAL para cultivar maíz. ¡Excelentes condiciones para una buena cosecha!',
      recommendations: [
        'Mantén el nivel actual de humedad',
        'Realiza rotación de cultivos',
        'Cosecha en 3-4 meses',
        'Controla malezas regularmente',
        'Aplica fertilizante nitrogenado'
      ],
      planting: 'Época ideal: Marzo - Abril',
      harvest: 'Cosecha en: 3-4 meses',
      tips: 'Necesita buena exposición solar'
    },
    frijol: {
      status: 'apta',
      description: '✅ Tu tierra es EXCELENTE para cultivar frijol. Condiciones óptimas para una buena producción.',
      recommendations: [
        'Mantén la humedad alrededor del 50%',
        'Usa tutores para las plantas',
        'Riega cada 2-3 días sin encharcar',
        'Cosecha en 2-3 meses',
        'Asocia con maíz para mejor crecimiento'
      ],
      planting: 'Época ideal: Mayo - Junio',
      harvest: 'Cosecha en: 2-3 meses',
      tips: 'Fija nitrógeno en el suelo naturalmente'
    },
    tomate: {
      status: 'moderadamente-apta',
      description: '⚠️ Tu tierra es aceptable para tomate, pero necesita más nutrientes para mejores resultados.',
      recommendations: [
        'Añade compost orgánico',
        'Usa soportes para las plantas',
        'Riega regularmente pero sin encharcar',
        'Protege del viento fuerte',
        'Controla plagas con insecticidas naturales'
      ],
      planting: 'Época ideal: Agosto - Septiembre',
      harvest: 'Cosecha en: 3-4 meses',
      tips: 'Requiere mucho sol y protección del viento'
    },
    zanahoria: {
      status: 'apta',
      description: '✅ Tu tierra es PERFECTA para zanahoria. ¡Excelente elección para una buena cosecha!',
      recommendations: [
        'Afloja bien la tierra antes de sembrar',
        'Mantén la tierra húmeda pero no empapada',
        'Aclara las plántulas cuando midan 5 cm',
        'Cosecha en 2-3 meses',
        'Usa suelos arenosos y bien drenados'
      ],
      planting: 'Época ideal: Todo el año',
      harvest: 'Cosecha en: 2-3 meses',
      tips: 'Suelo suelto sin piedras para raíces rectas'
    }
  };

  const generalTips = [
    {
      icon: '💧',
      title: 'Riego Inteligente',
      description: 'Riega temprano en la mañana o al atardecer. Usa riego por goteo para ahorrar agua.'
    },
    {
      icon: '🌱',
      title: 'Abono Natural',
      description: 'Usa compost casero con cáscaras de huevo, restos vegetales y café molido.'
    },
    {
      icon: '🔄',
      title: 'Rotación de Cultivos',
      description: 'Cambia los cultivos cada temporada para evitar agotar el suelo.'
    },
    {
      icon: '👀',
      title: 'Observación Constante',
      description: 'Revisa tus plantas diariamente para detectar plagas o enfermedades a tiempo.'
    },
    {
      icon: '🛡️',
      title: 'Protección Natural',
      description: 'Usa plantas compañeras como albahaca y caléndula para repeler plagas.'
    },
    {
      icon: '☀️',
      title: 'Luz Solar',
      description: 'Asegura que tus plantas reciban al menos 6 horas de sol directo al día.'
    }
  ];

  const handleCropSelect = (cropId) => {
    setSelectedCrop(cropId);
  };

  const handleFrequencyChange = (freq) => {
    setFrequency(freq);
    const newCrops = freq === "AM" ? amCrops : fmCrops;
    if (newCrops.length > 0) {
      setSelectedCrop(newCrops[0].id);
    }
  };

  const currentCrops = frequency === "AM" ? amCrops : fmCrops;
  const currentCrop = currentCrops.find(crop => crop.id === selectedCrop);
  const cropInfo = landSuitability[selectedCrop];

  return (
    <div className="home-container">
      <header className="radio-header">
        <h1>🌱 SembrandoBits</h1>
        <p>Tu asistente para entender y mejorar tus cultivos</p>
      </header>

      <main className="radio-main">
        <section className="radio-interface">
          <div className="radio-display">
            <div className="frequency-display">
              <span className="frequency-type">{frequency}</span>
              <span className="frequency-value">{currentCrop?.frequency}</span>
            </div>
            <div className="crop-display">
              <span className="crop-icon">{currentCrop?.icon}</span>
              <span className="crop-name">{currentCrop?.name}</span>
            </div>
          </div>

          <div className="radio-controls">
            <div className="frequency-selector">
              <button 
                className={`am-btn ${frequency === "AM" ? "active" : ""}`}
                onClick={() => handleFrequencyChange("AM")}
              >
                AM
              </button>
              <button 
                className={`fm-btn ${frequency === "FM" ? "active" : ""}`}
                onClick={() => handleFrequencyChange("FM")}
              >
                FM
              </button>
            </div>

            <div className="station-selector">
              {currentCrops.map(crop => (
                <button
                  key={crop.id}
                  className={`station-btn ${selectedCrop === crop.id ? "selected" : ""}`}
                  onClick={() => handleCropSelect(crop.id)}
                >
                  <span className="station-frequency">{crop.frequency}</span>
                  <span className="station-icon">{crop.icon}</span>
                  <span className="station-name">{crop.name}</span>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="crop-info">
          <div className="suitability-card">
            <h2>¿Mi tierra sirve para {currentCrop?.name}?</h2>
            <div className={`status-indicator ${cropInfo?.status}`}>
              {cropInfo?.status === 'apta' ? 
                <><span className="status-icon">✅</span> SÍ, TU TIERRA ES APTA</> : 
               cropInfo?.status === 'moderadamente-apta' ? 
                <><span className="status-icon">⚠️</span> PARCIALMENTE, CON AJUSTES</> : 
               <><span className="status-icon">❓</span> NO SÉ</>}
            </div>
            <p className="status-description">{cropInfo?.description}</p>
            
            <div className="crop-details">
              <div className="detail-item">
                <span className="detail-label">📅 Época de siembra:</span>
                <span className="detail-value">{cropInfo?.planting}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">⏰ Tiempo de cosecha:</span>
                <span className="detail-value">{cropInfo?.harvest}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">💡 Consejo rápido:</span>
                <span className="detail-value">{cropInfo?.tips}</span>
              </div>
            </div>
          </div>

          <div className="tabs-container">
            <div className="tabs-header">
              <button 
                className={`tab-btn ${activeTab === 'suelo' ? 'active' : ''}`}
                onClick={() => setActiveTab('suelo')}
              >
                📊 Datos del Sensor
              </button>
              <button 
                className={`tab-btn ${activeTab === 'recomendaciones' ? 'active' : ''}`}
                onClick={() => setActiveTab('recomendaciones')}
              >
                💡 Recomendaciones
              </button>
              <button 
                className={`tab-btn ${activeTab === 'consejos' ? 'active' : ''}`}
                onClick={() => setActiveTab('consejos')}
              >
                🌟 Consejos Generales
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'suelo' && (
                <div className="sensor-grid">
                  {sensorData[selectedCrop]?.map((data, index) => (
                    <div key={index} className="sensor-card">
                      <div className="sensor-type">{data.type}</div>
                      <div className="sensor-value">{data.value}</div>
                      <div className="sensor-status">{data.description}</div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'recomendaciones' && (
                <div className="recommendations-container">
                  <h3>Recomendaciones específicas para {currentCrop?.name}</h3>
                  <ul className="recommendations-list">
                    {cropInfo?.recommendations.map((rec, index) => (
                      <li key={index}>
                        <span className="bullet">📌</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {activeTab === 'consejos' && (
                <div className="general-tips">
                  <h3>Consejos generales para todos los cultivos</h3>
                  <div className="tips-grid">
                    {generalTips.map((tip, index) => (
                      <div key={index} className="tip-card">
                        <div className="tip-icon">{tip.icon}</div>
                        <h4>{tip.title}</h4>
                        <p>{tip.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Home;