import React from 'react';
import { GameState, GameRules } from '../types';
import { createInitialGameState } from '../gameLogic';

interface GameControlsProps {
  gameState: GameState;
  rules: GameRules;
  onGameStateChange: (newState: GameState) => void;
  onRulesChange: (rules: GameRules) => void;
}

export const GameControls: React.FC<GameControlsProps> = ({ 
  gameState, 
  rules, 
  onGameStateChange 
}) => {
  const handleNewGame = () => {
    const newGameState = createInitialGameState(rules);
    onGameStateChange(newGameState);
  };

  const handleResetGame = () => {
    const newGameState = createInitialGameState(rules);
    onGameStateChange(newGameState);
  };

  const handleUndoMove = () => {
    // This would require implementing move history
    // For now, just reset the game
    handleResetGame();
  };

  return (
    <div className="game-controls">
      <button 
        className="btn btn-success" 
        onClick={handleNewGame}
      >
        New Game
      </button>
      
      <button 
        className="btn btn-secondary" 
        onClick={handleResetGame}
      >
        Reset Game
      </button>
      
      <button 
        className="btn" 
        onClick={handleUndoMove}
        disabled={gameState.lastMove === null}
      >
        Undo Move
      </button>
    </div>
  );
};