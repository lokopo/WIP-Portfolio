import React from 'react';
import { GameState } from '../types';
import { getGameStatus } from '../gameLogic';

interface GameInfoProps {
  gameState: GameState;
}

export const GameInfo: React.FC<GameInfoProps> = ({ gameState }) => {
  const gameStatus = getGameStatus(gameState);
  
  return (
    <div className="game-info">
      <div className="current-player">
        {gameState.gameStatus === 'playing' 
          ? `Player ${gameState.currentPlayer + 1}'s Turn`
          : gameStatus
        }
      </div>
      
      <div className="game-status">
        <div>Player 1 Score: {gameState.goals[0]}</div>
        <div>Player 2 Score: {gameState.goals[1]}</div>
      </div>
      
      {gameState.lastMove && (
        <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
          Last move: Player {gameState.lastMove.player + 1} played pit {gameState.lastMove.pitIndex + 1}
          {gameState.lastMove.capturedStones > 0 && 
            ` (Captured ${gameState.lastMove.capturedStones} stones)`
          }
          {gameState.lastMove.extraTurn && ' (Extra turn!)'}
        </div>
      )}
    </div>
  );
};