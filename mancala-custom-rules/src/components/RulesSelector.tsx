import React from 'react';
import { RuleSet, GameRules } from '../types';
import { RULE_SETS } from '../rules';

interface RulesSelectorProps {
  currentRules: GameRules;
  onRulesChange: (rules: GameRules) => void;
}

export const RulesSelector: React.FC<RulesSelectorProps> = ({ currentRules, onRulesChange }) => {
  const handleRuleSetChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedRuleSet = RULE_SETS.find(ruleSet => ruleSet.id === event.target.value);
    if (selectedRuleSet) {
      onRulesChange(selectedRuleSet.rules);
    }
  };

  const getCurrentRuleSet = (): RuleSet | undefined => {
    return RULE_SETS.find(ruleSet => 
      JSON.stringify(ruleSet.rules) === JSON.stringify(currentRules)
    );
  };

  const currentRuleSet = getCurrentRuleSet();

  return (
    <div className="rules-selector">
      <label htmlFor="rules-select" style={{ color: 'white', marginRight: '10px' }}>
        Select Rule Set:
      </label>
      <select
        id="rules-select"
        value={currentRuleSet?.id || 'standard'}
        onChange={handleRuleSetChange}
      >
        {RULE_SETS.map(ruleSet => (
          <option key={ruleSet.id} value={ruleSet.id}>
            {ruleSet.name}
          </option>
        ))}
      </select>
      
      {currentRuleSet && (
        <div className="rules-description">
          <h4>{currentRuleSet.name}</h4>
          <p>{currentRuleSet.description}</p>
        </div>
      )}
    </div>
  );
};