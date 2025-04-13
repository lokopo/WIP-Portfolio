# Space Engineers Linux Diagnostics Tool

This tool helps diagnose crashes and issues with Space Engineers running on Linux through Steam/Proton.

## Features

- Analyzes Space Engineers log files for common crash patterns
- Gathers system information (CPU, RAM, GPU)
- Checks Proton version and configuration
- Provides targeted recommendations based on found issues

## Requirements

- Python 3.6 or higher
- Space Engineers installed via Steam
- Linux system with Steam and Proton

## Installation

1. Clone this repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Simply run the diagnostic script:
```bash
python se_diagnostics.py
```

The tool will automatically:
1. Locate Space Engineers installation
2. Analyze log files
3. Generate a diagnostic report
4. Provide recommendations based on findings 