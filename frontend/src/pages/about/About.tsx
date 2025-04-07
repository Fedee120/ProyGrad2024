import React from 'react';
import Layout from "../layout";
import './About.css';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const About = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/login');
  };

  const AboutContent = () => (
    <div className="about-content">
      {!currentUser && (
        <div className="back-button-container">
          <button onClick={handleBack} className="back-button">
            <svg 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M19 12H5" />
              <path d="M12 19l-7-7 7-7" />
            </svg>
            Volver
          </button>
        </div>
      )}
      <h1>Sobre el Proyecto</h1>
      
      <div className="about-text">
        <p>
          Bienvenido/a a este proyecto de grado, desarrollado en el marco de la Facultad de Ingeniería de la Universidad de la República (UdelaR) en Uruguay. Este trabajo fue realizado en el año 2024-2025 por Federico Gil, Agustina Moraes y William Tift, bajo la tutoría de Regina Motz y con la co-tutoría de Libertad Tansini.
        </p>
        
        <p>
          La iniciativa forma parte de los requerimientos académicos para la obtención del título, y tiene como objetivo explorar y aplicar tecnologías de inteligencia artificial. En particular, se centra en el diseño e implementación de un chatbot generativo, concebido para asistir a docentes en la comprensión y uso de la IA generativa, apoyándose en información curada y en estrategias pedagógicas innovadoras.
        </p>
        
        <p>
          El proyecto surge de la necesidad de facilitar la integración de herramientas tecnológicas en el proceso de enseñanza y aprendizaje, brindando respuestas claras y fundamentadas que promuevan el pensamiento crítico y la reflexión. Aunque en este sitio no se detallan aspectos técnicos, la investigación y desarrollo realizado respalda nuestro compromiso con la calidad, la usabilidad y la seguridad de la información. Los documentos que fundamentan las respuestas fueron cuidadosamente seleccionados para garantizar la precisión y calidad de la información. Estos documentos son abiertos y de dominio público.
        </p>
        
        <p>
          Agradecemos tus sugerencias y comentarios para seguir mejorando esta iniciativa. Si deseas aportar ideas o expresar alguna inquietud, por favor, contáctanos a través del correo: <a href="mailto:rmotz@fing.edu.uy">rmotz@fing.edu.uy</a>.
        </p>
        
        <p className="thank-you">
          ¡Gracias por tu interés y bienvenido/a a esta experiencia de innovación educativa!
        </p>
      </div>
    </div>
  );

  // If user is not authenticated, render without layout
  if (!currentUser) {
    return (
      <div className="about-container">
        <AboutContent />
      </div>
    );
  }

  // If user is authenticated, wrap with layout
  return (
    <Layout>
      <div className="about-container">
        <AboutContent />
      </div>
    </Layout>
  );
};

export default About; 