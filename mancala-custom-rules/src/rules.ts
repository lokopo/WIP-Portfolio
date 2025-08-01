import { RuleSet, GameRules } from './types';

export const DEFAULT_RULES: GameRules = {
  stonesPerPit: 4,
  pitsPerPlayer: 6,
  distributeToGoals: true,
  skipOpponentGoal: false,
  captureEnabled: true,
  captureOnEmpty: true,
  captureOnLastStone: false,
  carryOnEnabled: false,
  carryOnUntilEmpty: false,
  extraTurnOnGoal: true,
  extraTurnOnCapture: false,
  collectRemainingStones: true,
  winnerDetermination: 'mostStones'
};

export const CARRY_ON_RULES: GameRules = {
  ...DEFAULT_RULES,
  carryOnEnabled: true,
  carryOnUntilEmpty: true,
  captureEnabled: false, // Disable capture for carry-on rules
  name: 'Carry On Rules'
};

export const STANDARD_MANCALA_RULES: GameRules = {
  ...DEFAULT_RULES,
  name: 'Standard Mancala'
};

export const CAPTURE_FOCUSED_RULES: GameRules = {
  ...DEFAULT_RULES,
  captureEnabled: true,
  captureOnEmpty: true,
  captureOnLastStone: true,
  extraTurnOnCapture: true,
  name: 'Capture Focused'
};

export const NO_CAPTURE_RULES: GameRules = {
  ...DEFAULT_RULES,
  captureEnabled: false,
  name: 'No Capture'
};

export const RULE_SETS: RuleSet[] = [
  {
    id: 'standard',
    name: 'Standard Mancala',
    description: 'Traditional Mancala rules with capture mechanics and extra turns for landing in your goal.',
    rules: STANDARD_MANCALA_RULES
  },
  {
    id: 'carry-on',
    name: 'Carry On Rules',
    description: 'After placing the last stone, pick up all stones from that pit and continue distributing until you reach an empty pit or land in your goal.',
    rules: CARRY_ON_RULES
  },
  {
    id: 'capture-focused',
    name: 'Capture Focused',
    description: 'Enhanced capture mechanics with extra turns for successful captures.',
    rules: CAPTURE_FOCUSED_RULES
  },
  {
    id: 'no-capture',
    name: 'No Capture',
    description: 'Simplified rules without capture mechanics, focusing on strategic distribution.',
    rules: NO_CAPTURE_RULES
  }
];

export function getRuleSet(id: string): RuleSet | undefined {
  return RULE_SETS.find(ruleSet => ruleSet.id === id);
}

export function getDefaultRuleSet(): RuleSet {
  return RULE_SETS[0];
}