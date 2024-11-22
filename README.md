# LocalComputerUse

Local Computer Use with Samsung's TinyClick and Ollama. An intelligent screen interaction tool that uses AI to understand natural language commands and execute corresponding actions on your screen.

## 🌟 Features

- Natural language command processing
- Real-time screen capture and analysis
- AI-powered click point detection
- Automated mouse control execution
- Support for both CPU and GPU processing

## 🔧 Requirements

- Python 3.7+
- PyTorch
- Transformers
- Pillow (PIL)
- PyAutoGUI
- CUDA (optional, for GPU acceleration)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/LexiestLeszek/LocalComputerUse.git
cd LocalComputerUse
```

2. Install the required packages:
```bash
pip install torch transformers Pillow pyautogui
```

## 🚀 Usage

1. Run the main script:
```bash
python main.py
```

2. Enter your query

3. Hope that it will not use sudo rm rf

4. Type 'quit' to exit the program

## 🧠 How It Works

0. **Plan generation**: Uses Ollama and LLMs to generate a step by step plan to achieve a goal.

1. **Screenshot Capture**: Uses PyAutoGUI to capture the current screen state

2. **Input Processing**: 
   - Converts the screenshot to RGB format
   - Processes the natural language command
   - Prepares inputs for the AI model

3. **AI Analysis**:
   - Uses the Samsung/TinyClick model
   - Analyzes the screenshot and command
   - Determines the appropriate click location

4. **Action Execution**:
   - Converts the model's output to screen coordinates
   - Executes the mouse click at the determined location

