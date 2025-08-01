export interface GameState {
  board: number[][];
  goals: [number, number]; // [player1Goal, player2Goal]
  currentPlayer: 0 | 1;
  gameStatus: 'playing' | 'finished';
  winner: number | null;
  lastMove: MoveResult | null;
}

export interface MoveResult {
  player: number;
  pitIndex: number;
  stonesDistributed: number[];
  capturedStones: number;
  extraTurn: boolean;
  gameEnded: boolean;
}

export interface RuleSet {
  id: string;
  name: string;
  description: string;
  rules: GameRules;
}

export interface GameRules {
  // Basic game parameters
  stonesPerPit: number;
  pitsPerPlayer: number;
  
  // Distribution rules
  distributeToGoals: boolean;
  skipOpponentGoal: boolean;
  
  // Capture rules
  captureEnabled: boolean;
  captureOnEmpty: boolean;
  captureOnLastStone: boolean;
  
  // Special rules
  carryOnEnabled: boolean;
  carryOnUntilEmpty: boolean;
  
  // Turn rules
  extraTurnOnGoal: boolean;
  extraTurnOnCapture: boolean;
  
  // End game rules
  collectRemainingStones: boolean;
  winnerDetermination: 'mostStones' | 'mostGoals' | 'custom';
  
  // Display name
  name?: string;
}

export interface CustomRule {
  id: string;
  name: string;
  description: string;
  ruleFunction: (gameState: GameState, moveResult: MoveResult) => GameState;
}

export type Player = 0 | 1;