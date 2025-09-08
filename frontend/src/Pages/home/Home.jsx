import React from "react";
import "./stylehome.css";

function Home() {
  return (
    <article>
      <div className="sectionWrapper">
        <div id="_boxes">
          <ul>
            <li>
              <figure>
                <h2>Primera Caja</h2>
                <figcaption>
                  Texto descriptivo de la primera tarjeta. Aquí puedes colocar información breve.
                </figcaption>
                <a href="#">
                  <em>Leer más</em> <i>➜</i>
                </a>
              </figure>
              <svg>
                <rect width="100%" height="100%" stroke="var(--cardAccent)" strokeWidth="4" fill="none"></rect>
              </svg>
            </li>

            <li>
              <figure>
                <h2>Segunda Caja</h2>
                <figcaption>
                  Texto descriptivo de la segunda tarjeta. Puedes agregar más detalles aquí.
                </figcaption>
                <a href="#">
                  <em>Leer más</em> <i>➜</i>
                </a>
              </figure>
              <svg>
                <rect width="100%" height="100%" stroke="var(--cardAccent)" strokeWidth="4" fill="none"></rect>
              </svg>
            </li>

            <li>
              <figure>
                <h2>Tercera Caja</h2>
                <figcaption>
                  Texto descriptivo de la tercera tarjeta. Un pequeño resumen o detalle.
                </figcaption>
                <a href="#">
                  <em>Leer más</em> <i>➜</i>
                </a>
              </figure>
              <svg>
                <rect width="100%" height="100%" stroke="var(--cardAccent)" strokeWidth="4" fill="none"></rect>
              </svg>
            </li>
          </ul>
        </div>
      </div>
    </article>
  );
}

export default Home;
