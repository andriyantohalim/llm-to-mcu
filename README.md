# LLM to MCU - AI-Powered Serial Device Control

A Python project that enables natural language control of microcontroller devices through serial communication, powered by Large Language Models (LLMs) using Ollama.

## 🚀 Features

- **Serial Communication**: Direct control of MCU devices via USB/serial ports
- **AI-Powered Interface**: Natural language processing using Ollama LLMs
- **Multiple Control Methods**:
  - Direct serial commands
  - Simple AI agent with intent parsing
  - Advanced LangGraph-based agentic AI
- **LED Control**: Turn LEDs on/off and check device status
- **Cross-Platform**: Works on macOS, Linux, and Windows

## 📋 Requirements

- Python 3.8+
- Ollama installed and running
- MCU device connected via USB/serial
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-to-mcu
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and setup Ollama**:
   ```bash
   # Install Ollama (macOS/Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model (e.g., llama3.2 or gpt-oss:20b)
   ollama pull llama3.2
   ollama pull gpt-oss:20b
   ```

5. **Find your serial port**:
   ```bash
   # macOS/Linux
   ls /dev/cu.*
   ls /dev/tty.*
   
   # Windows
   # Check Device Manager for COM ports
   ```

## 🎯 Usage

### 1. Direct Serial Control

Basic serial communication without AI:

```bash
python main.py
```

This provides:
- Direct LED on/off commands
- Status checking
- Interactive command mode

### 2. Simple AI Agent

Natural language control with intent parsing:

```bash
python simple_ai_agent.py
```

Example interactions:
- **You**: "Please turn on the LED"
- **AI**: "✅ Sure! I've turned on the LED for you."

- **You**: "What's the device status?"
- **AI**: "📊 The device shows: LED is currently ON"

### 3. Advanced LangGraph Agent

Full agentic AI with tool usage and state management:

```bash
python ai_agent.py
```

Features:
- Advanced conversation flow
- Tool execution tracking
- State-based decision making

## 🔧 Configuration

### Serial Port Configuration

Update the serial port in the respective files:

```python
# Default ports by platform:
# macOS: /dev/cu.usbmodem* or /dev/cu.usbserial-*
# Linux: /dev/ttyUSB* or /dev/ttyACM*
# Windows: COM1, COM2, etc.

controller = SerialController(port='/dev/cu.usbmodem21102', baudrate=9600)
```

### Ollama Model Selection

Supported models:
- `llama3.2` (recommended for general use)
- `gpt-oss:20b` (larger model, better understanding)
- `mistral` (alternative option)
- Any other Ollama-compatible model

## 📁 Project Structure

```
llm-to-mcu/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # Direct serial control
├── simple_ai_agent.py       # Simple AI with intent parsing
├── ai_agent.py              # Advanced LangGraph agent
├── serial_controller.py     # Serial communication class
└── venv/                    # Virtual environment
```

## 🔌 Hardware Setup

### Supported Commands

The system expects your MCU to respond to these serial commands:

1. **LED Control**:
   - `led on` - Turn LED on
   - `led off` - Turn LED off

2. **Status Check**:
   - `status` - Get current device status

### Arduino Example

```cpp
void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "led on") {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED ON");
    }
    else if (command == "led off") {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED OFF");
    }
    else if (command == "status") {
      bool ledState = digitalRead(LED_BUILTIN);
      Serial.println(ledState ? "LED is ON" : "LED is OFF");
    }
  }
}
```

## 🤖 AI Agent Features

### Intent Recognition

The AI agents can understand various ways to express commands:

**Turn LED On**:
- "Please turn on the LED"
- "Switch on the light"
- "Enable the LED"
- "Activate the LED"

**Turn LED Off**:
- "Turn off the LED"
- "Switch off the light"
- "Disable the LED"
- "Deactivate the LED"

**Check Status**:
- "What's the status?"
- "Check the LED state"
- "How is the device?"
- "Current condition?"

### Response Generation

The AI provides natural, conversational responses:
- Confirms actions taken
- Reports device responses
- Handles errors gracefully
- Maintains conversation context

## 🛠️ Troubleshooting

### Common Issues

1. **Serial Port Not Found**:
   ```bash
   # Check available ports
   ls /dev/cu.*  # macOS
   ls /dev/tty*  # Linux
   ```

2. **Permission Denied (Linux/macOS)**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0  # Replace with your port
   # Or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

3. **Ollama Connection Error**:
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Start Ollama service
   ollama serve
   ```

4. **Model Not Found**:
   ```bash
   # Pull the required model
   ollama pull llama3.2
   ```

### Debug Mode

Enable verbose logging by modifying the serial controller:

```python
# In serial_controller.py, set debug=True
def send_command(self, command, debug=True):
    if debug:
        print(f"DEBUG: Sending '{command}'")
    # ... rest of the method
```

## 🚀 Extending the Project

### Adding New Commands

1. **Update MCU firmware** to handle new commands
2. **Add methods** to `SerialController` class:
   ```python
   def custom_command(self):
       return self.send_command("custom")
   ```
3. **Update AI prompts** to recognize new intents
4. **Add tool functions** for LangGraph integration

### Supporting New Devices

The project can be extended to control various devices:
- Servo motors
- Sensors
- Displays
- Relays
- Motor controllers

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [LangChain](https://python.langchain.com/) for AI agent framework
- [LangGraph](https://python.langchain.com/docs/langgraph) for stateful agent workflows
- [PySerial](https://pyserial.readthedocs.io/) for serial communication

---

**Happy coding! 🚀**