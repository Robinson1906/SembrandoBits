import React from "react";
import { Link } from "react-router-dom";


function Navbar() {
  return (
    <nav className="navbar">
      <h1 className="logo">🌱 SembrandoBits</h1>
      <ul className="nav-links">
        <li>
          <Link to="/">Home</Link>
        </li>
        <li>
          <Link to="/sensores">Sensores</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;
