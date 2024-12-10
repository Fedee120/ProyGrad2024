import React from 'react';
import './Suggestions.css';

interface SuggestionsProps {
  suggestions: string[];
  isLoading: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

const Suggestions: React.FC<SuggestionsProps> = ({
  suggestions,
  isLoading,
  onSuggestionClick,
}) => {
  // Calcular el espacio necesario para móviles
  // Altura de cada sugerencia (32px) + gap (6px) + padding superior e inferior del contenedor (12px)
  const spacerHeight = isLoading 
    ? 44 // Altura para el estado de carga
    : suggestions.length > 0 
      ? (suggestions.length * 32) + ((suggestions.length - 1) * 6) + 12
      : 0;

  return (
    <>
      {/* Espaciador para móviles */}
      <div className="suggestions-spacer" style={{ height: `${spacerHeight}px` }} />
      
      <div className="suggestions-container">
        {isLoading ? (
          <div className="suggestion-bubble loading">
            Generando sugerencias...
          </div>
        ) : suggestions.length > 0 ? (
          suggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-bubble"
              onClick={() => onSuggestionClick(suggestion)}
            >
              {suggestion}
            </button>
          ))
        ) : null}
      </div>
    </>
  );
};

export default Suggestions; 