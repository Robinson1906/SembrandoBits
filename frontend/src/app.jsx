import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Components/Navbar";
import Footer from "./Components/Footer";
import Home from "./Pages/home/Home";
import Cultivos from "./Pages/cultivos/Cultivos";
import TipoTierra from "./Pages/Tierras/TipoTierra";
import Sensores from "./Pages/Sensores/Sensores";


function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/sensores" element={<Sensores />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
