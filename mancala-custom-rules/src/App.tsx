import { useState, useEffect } from 'react';
import { GameState, GameRules } from './types';
import { createInitialGameState } from './gameLogic';
import { getDefaultRuleSet } from './rules';
import { GameBoard } from './components/GameBoard';
import { GameControls } from './components/GameControls';
import { RulesSelector } from './components/RulesSelector';
import { GameInfo } from './components/GameInfo';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [currentRules, setCurrentRules] = useState<GameRules>(getDefaultRuleSet().rules);

  useEffect(() => {
    // Initialize game with default rules
    const initialGameState = createInitialGameState(currentRules);
    setGameState(initialGameState);
  }, []);

  const handleGameStateChange = (newState: GameState) => {
    setGameState(newState);
  };

  const handleRulesChange = (newRules: GameRules) => {
    setCurrentRules(newRules);
    // Reset game with new rules
    const newGameState = createInitialGameState(newRules);
    setGameState(newGameState);
  };

  if (!gameState) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container">
      <div className="game-header">
        <h1>Mancala Custom Rules</h1>
        <p>A customizable Mancala game with multiple rule sets</p>
      </div>

      <RulesSelector 
        currentRules={currentRules}
        onRulesChange={handleRulesChange}
      />

      <GameControls 
        gameState={gameState}
        rules={currentRules}
        onGameStateChange={handleGameStateChange}
        onRulesChange={handleRulesChange}
      />

      <GameBoard 
        gameState={gameState}
        rules={currentRules}
        onGameStateChange={handleGameStateChange}
      />

      <GameInfo gameState={gameState} />
    </div>
  );
}

export default App;