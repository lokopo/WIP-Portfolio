import { GameState, MoveResult, GameRules, Player } from './types';

export function createInitialGameState(rules: GameRules): GameState {
  const board = Array(2).fill(null).map(() => Array(rules.pitsPerPlayer).fill(rules.stonesPerPit));
  
  return {
    board,
    goals: [0, 0],
    currentPlayer: 0,
    gameStatus: 'playing',
    winner: null,
    lastMove: null
  };
}



export function isValidMove(gameState: GameState, player: Player, pitIndex: number, rules: GameRules): boolean {
  if (gameState.gameStatus !== 'playing') return false;
  if (gameState.currentPlayer !== player) return false;
  if (pitIndex < 0 || pitIndex >= rules.pitsPerPlayer) return false;
  if (gameState.board[player][pitIndex] === 0) return false;
  
  return true;
}

export function makeMove(gameState: GameState, player: Player, pitIndex: number, rules: GameRules): MoveResult {
  if (!isValidMove(gameState, player, pitIndex, rules)) {
    throw new Error('Invalid move');
  }

  const newBoard = gameState.board.map(row => [...row]);
  const newGoals = [...gameState.goals] as [number, number];
  
  let stones = newBoard[player][pitIndex];
  newBoard[player][pitIndex] = 0;
  
  let currentPlayer = player;
  let currentPit = pitIndex + 1;
  let stonesDistributed: number[] = [];
  let capturedStones = 0;
  let extraTurn = false;
  let gameEnded = false;
  
  // Distribute stones
  while (stones > 0) {
    // Check if we need to move to the next row
    if (currentPit >= rules.pitsPerPlayer) {
      // Check if we can place in our own goal
      if (currentPlayer === player && rules.distributeToGoals) {
        newGoals[player]++;
        stonesDistributed.push(-1); // -1 indicates goal
        stones--;
        if (stones === 0) {
          extraTurn = rules.extraTurnOnGoal;
          break;
        }
      }
      
      // Move to opponent's row
      currentPlayer = currentPlayer === 0 ? 1 : 0;
      currentPit = 0;
    }
    
    // Skip opponent's goal if needed
    if (currentPit === rules.pitsPerPlayer && currentPlayer !== player && rules.skipOpponentGoal) {
      currentPlayer = currentPlayer === 0 ? 1 : 0;
      currentPit = 0;
    }
    
    // Place stone in pit
    if (currentPit < rules.pitsPerPlayer) {
      newBoard[currentPlayer][currentPit]++;
      stonesDistributed.push(currentPit);
      stones--;
      
      // Handle carry-on rules
      if (stones === 0 && rules.carryOnEnabled) {
        const lastPitStones = newBoard[currentPlayer][currentPit];
        if (lastPitStones > 1 && rules.carryOnUntilEmpty) {
          stones = lastPitStones;
          newBoard[currentPlayer][currentPit] = 0;
          continue;
        }
      }
      
      // Handle capture
      if (stones === 0 && rules.captureEnabled && currentPlayer === player) {
        const oppositePit = rules.pitsPerPlayer - 1 - currentPit;
        const oppositePlayer = currentPlayer === 0 ? 1 : 0;
        
        if (newBoard[currentPlayer][currentPit] === 1 && 
            newBoard[oppositePlayer][oppositePit] > 0 &&
            (rules.captureOnEmpty || rules.captureOnLastStone)) {
          
          capturedStones = newBoard[oppositePlayer][oppositePit] + 1;
          newGoals[player] += capturedStones;
          newBoard[oppositePlayer][oppositePit] = 0;
          newBoard[currentPlayer][currentPit] = 0;
          
          if (rules.extraTurnOnCapture) {
            extraTurn = true;
          }
        }
      }
    }
    
    currentPit++;
  }
  
  // Check if game is over
  const player1Stones = newBoard[0].reduce((sum, stones) => sum + stones, 0);
  const player2Stones = newBoard[1].reduce((sum, stones) => sum + stones, 0);
  
  if (player1Stones === 0 || player2Stones === 0) {
    gameEnded = true;
    
    if (rules.collectRemainingStones) {
      newGoals[0] += player1Stones;
      newGoals[1] += player2Stones;
      newBoard[0] = newBoard[0].map(() => 0);
      newBoard[1] = newBoard[1].map(() => 0);
    }
  }
  
  const moveResult: MoveResult = {
    player,
    pitIndex,
    stonesDistributed,
    capturedStones,
    extraTurn,
    gameEnded
  };
  
  return moveResult;
}

export function applyMoveResult(gameState: GameState, moveResult: MoveResult, rules: GameRules): GameState {
  const newGameState: GameState = {
    board: gameState.board.map(row => [...row]),
    goals: [...gameState.goals] as [number, number],
    currentPlayer: gameState.currentPlayer,
    gameStatus: gameState.gameStatus,
    winner: gameState.winner,
    lastMove: moveResult
  };
  
  // Apply the move result to the game state
  if (moveResult.gameEnded) {
    newGameState.gameStatus = 'finished';
    newGameState.winner = determineWinner(newGameState, rules);
  } else if (!moveResult.extraTurn) {
    newGameState.currentPlayer = newGameState.currentPlayer === 0 ? 1 : 0;
  }
  
  return newGameState;
}

export function determineWinner(gameState: GameState, rules: GameRules): number | null {
  if (rules.winnerDetermination === 'mostStones') {
    if (gameState.goals[0] > gameState.goals[1]) return 0;
    if (gameState.goals[1] > gameState.goals[0]) return 1;
    return null; // Tie
  } else if (rules.winnerDetermination === 'mostGoals') {
    // This would be for games where goals are scored differently
    return gameState.goals[0] > gameState.goals[1] ? 0 : 1;
  }
  
  return null;
}

export function getGameStatus(gameState: GameState): string {
  if (gameState.gameStatus === 'finished') {
    if (gameState.winner === null) {
      return 'Game ended in a tie!';
    }
    return `Player ${gameState.winner + 1} wins!`;
  }
  
  return `Player ${gameState.currentPlayer + 1}'s turn`;
}

export function canPlayerMove(gameState: GameState, player: Player): boolean {
  if (gameState.gameStatus !== 'playing') return false;
  if (gameState.currentPlayer !== player) return false;
  
  return gameState.board[player].some(stones => stones > 0);
}

export function getValidMoves(gameState: GameState, player: Player): number[] {
  if (gameState.gameStatus !== 'playing') return [];
  if (gameState.currentPlayer !== player) return [];
  
  return gameState.board[player]
    .map((stones, index) => ({ stones, index }))
    .filter(({ stones }) => stones > 0)
    .map(({ index }) => index);
}