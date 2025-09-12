import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Components/Navbar";
import Footer from "./Components/Footer";
import Home from "./Pages/home/Home";       // 👈 cambiado
import Cultivos from "./Pages/cultivos/Cultivos";
import TipoTierra from "./Pages/Tierras/TipoTierra";
import Sensores from "./Pages/Sensores/Sensores";


function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        
        <main className="flex-grow p-6 bg-gray-50">
          <Routes>
            <Route path="/" element={<Home />} />          {/* 👈 cambiado */}
              <Route path="/Sensores" element={<Sensores />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
