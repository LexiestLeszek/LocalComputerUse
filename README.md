# LocalComputerUse

Local Computer Use with Samsung's TinyClick. An intelligent screen interaction tool that uses AI to understand natural language commands and execute corresponding actions on your screen.

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

2. Enter your command when prompted. For example:
   - "Click the close button"
   - "Click the search bar"
   - "Click the menu icon"

3. The program will:
   - Take a screenshot after a 3-second delay
   - Analyze the screenshot using AI
   - Execute the requested action

4. Type 'quit' to exit the program

## 🧠 How It Works

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

## 🛠️ Technical Details

- Model: Samsung/TinyClick
- Input Processing: Automatic image resizing and text encoding
- Coordinate System: Uses a 1000x1000 normalized coordinate space
- Output Format: Action dictionary containing action type and click coordinates

## ⚠️ Limitations

- Currently only supports click actions
- Requires clear visual elements on screen
- May have varying accuracy depending on screen content
- Performance depends on hardware capabilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Samsung for the TinyClick model
- Hugging Face Transformers team
- PyAutoGUI developers

## 📞 Contact

For questions and support, please open an issue in the GitHub repository.
```

This README provides:
- Clear installation instructions
- Usage examples
- Technical details
- Project limitations
- Contributing guidelines
- License information
- Acknowledgments

You can customize it further by:
- Adding specific examples with screenshots
- Including more detailed troubleshooting steps
- Adding badges (build status, version, etc.)
- Including more specific contribution guidelines
- Adding a roadmap for future features
