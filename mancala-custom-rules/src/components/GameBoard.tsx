import React from 'react';
import { GameState, Player, GameRules } from '../types';
import { isValidMove, makeMove, applyMoveResult } from '../gameLogic';

interface GameBoardProps {
  gameState: GameState;
  rules: GameRules;
  onGameStateChange: (newState: GameState) => void;
}

export const GameBoard: React.FC<GameBoardProps> = ({ gameState, rules, onGameStateChange }) => {
  const handlePitClick = (player: Player, pitIndex: number) => {
    if (!isValidMove(gameState, player, pitIndex, rules)) {
      return;
    }

    try {
      const moveResult = makeMove(gameState, player, pitIndex, rules);
      const newGameState = applyMoveResult(gameState, moveResult, rules);
      onGameStateChange(newGameState);
    } catch (error) {
      console.error('Invalid move:', error);
    }
  };

  const renderPit = (player: Player, pitIndex: number, stones: number) => {
    const isCurrentPlayer = gameState.currentPlayer === player;
    const isEmpty = stones === 0;
    
    const pitClass = `pit ${isCurrentPlayer ? 'active' : ''} ${isEmpty ? 'empty' : ''}`;
    
    return (
      <div
        key={`${player}-${pitIndex}`}
        className={pitClass}
        onClick={() => handlePitClick(player, pitIndex)}
        title={`Player ${player + 1}, Pit ${pitIndex + 1}: ${stones} stones`}
      >
        <span className="pit-stones">{stones}</span>
      </div>
    );
  };

  const renderGoal = (player: Player, stones: number) => {
    return (
      <div key={`goal-${player}`} className="goal">
        <div className="goal-stones">{stones}</div>
        <div style={{ fontSize: '0.8rem', color: '#8b4513' }}>
          Player {player + 1}
        </div>
      </div>
    );
  };

  return (
    <div className="game-board">
      <div className="mancala-board">
        {/* Player 2's goal */}
        {renderGoal(1, gameState.goals[1])}
        
        <div className="player-pits">
          {/* Player 2's pits (top row) */}
          <div className="pit-row">
            {gameState.board[1].map((stones, index) => 
              renderPit(1, index, stones)
            )}
          </div>
          
          {/* Player 1's pits (bottom row) */}
          <div className="pit-row">
            {gameState.board[0].map((stones, index) => 
              renderPit(0, index, stones)
            )}
          </div>
        </div>
        
        {/* Player 1's goal */}
        {renderGoal(0, gameState.goals[0])}
      </div>
    </div>
  );
};