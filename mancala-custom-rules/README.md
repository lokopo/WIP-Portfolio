# Mancala Custom Rules

A customizable Mancala game built with React and TypeScript that supports multiple rule sets, including the unique "Carry On" rules.

## Features

- **Multiple Rule Sets**: Choose from different Mancala variants
- **Carry On Rules**: After placing the last stone, pick up all stones from that pit and continue distributing
- **Standard Mancala**: Traditional rules with capture mechanics
- **Capture Focused**: Enhanced capture mechanics with extra turns
- **No Capture**: Simplified rules without capture mechanics
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Customizable**: Easy to add new rule sets and modify existing ones

## Rule Sets

### Standard Mancala
Traditional Mancala rules with capture mechanics and extra turns for landing in your goal.

### Carry On Rules
After placing the last stone, pick up all stones from that pit and continue distributing until you reach an empty pit or land in your goal.

### Capture Focused
Enhanced capture mechanics with extra turns for successful captures.

### No Capture
Simplified rules without capture mechanics, focusing on strategic distribution.

## Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mancala-custom-rules
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:3000`

## How to Play

1. **Select a Rule Set**: Choose from the dropdown menu at the top
2. **Start a Game**: Click "New Game" to begin
3. **Make Moves**: Click on any pit on your side (bottom row for Player 1, top row for Player 2)
4. **Follow the Rules**: Each rule set has different mechanics:
   - **Standard**: Capture opponent's stones when landing in an empty pit
   - **Carry On**: Continue distributing stones from the last pit you placed a stone in
   - **Capture Focused**: Enhanced capture mechanics with extra turns
   - **No Capture**: Focus on strategic distribution without captures

## Game Mechanics

### Basic Rules
- Each player has 6 pits and 1 goal
- Players take turns picking up all stones from one of their pits
- Stones are distributed one by one in a counter-clockwise direction
- The game ends when one player has no stones left in their pits

### Carry On Rules (Special Feature)
When you place the last stone in a pit that contains other stones, you pick up all stones from that pit and continue distributing them. This continues until you reach an empty pit or place a stone in your goal.

### Capture Rules
- Land in an empty pit on your side to capture stones from the opposite pit
- Captured stones go to your goal
- Some rule sets give extra turns for successful captures

## Project Structure

```
src/
├── components/          # React components
│   ├── GameBoard.tsx   # Main game board
│   ├── GameControls.tsx # Game control buttons
│   ├── GameInfo.tsx    # Game status display
│   └── RulesSelector.tsx # Rule set selection
├── types.ts            # TypeScript type definitions
├── rules.ts            # Rule set definitions
├── gameLogic.ts        # Core game logic
├── App.tsx             # Main application component
└── index.css           # Styles
```

## Adding Custom Rules

The game is designed to be easily extensible. To add a new rule set:

1. Define the rules in `src/rules.ts`:
```typescript
export const MY_CUSTOM_RULES: GameRules = {
  ...DEFAULT_RULES,
  // Add your custom rule properties
  customProperty: true,
  name: 'My Custom Rules'
};
```

2. Add the rule set to the `RULE_SETS` array:
```typescript
export const RULE_SETS: RuleSet[] = [
  // ... existing rule sets
  {
    id: 'my-custom',
    name: 'My Custom Rules',
    description: 'Description of your custom rules',
    rules: MY_CUSTOM_RULES
  }
];
```

3. Implement any custom logic in `src/gameLogic.ts` if needed.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS3** - Styling with modern features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.