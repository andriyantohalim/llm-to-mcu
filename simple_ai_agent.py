import ollama
import re
from serial_controller import SerialController

class SimpleAIAgent:
    def __init__(self, model_name="gpt-oss:20b"):
        self.model_name = model_name
        self.serial_controller = None
        
    def initialize_serial(self, port='/dev/cu.usbmodem21102', baudrate=9600):
        """Initialize the serial controller"""
        try:
            self.serial_controller = SerialController(port=port, baudrate=baudrate)
            print(f"✅ Serial connection established on {port}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize serial connection: {e}")
            return False
    
    def parse_intent(self, user_input):
        """Parse user intent using Ollama"""
        system_prompt = """You are an intent classifier for LED control commands. 
        Analyze the user input and respond with exactly one of these actions:
        - "LED_ON" if user wants to turn on/enable/activate the LED
        - "LED_OFF" if user wants to turn off/disable/deactivate the LED  
        - "STATUS" if user wants to check status/state/condition
        - "UNKNOWN" if unclear or unrelated

        Examples:
        "please turn on the led" -> LED_ON
        "turn off the light" -> LED_OFF
        "what's the status?" -> STATUS
        "hello" -> UNKNOWN

        Respond with only the action word, nothing else."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content'].strip().upper()
        except Exception as e:
            print(f"Error parsing intent: {e}")
            return "UNKNOWN"
    
    def execute_command(self, intent):
        """Execute the appropriate serial command"""
        if self.serial_controller is None:
            return "❌ Serial connection not initialized"
        
        if intent == "LED_ON":
            response = self.serial_controller.led_on()
            return f"✅ LED turned ON. Device response: {response}" if response else "✅ LED ON command sent"
        
        elif intent == "LED_OFF":
            response = self.serial_controller.led_off()
            return f"✅ LED turned OFF. Device response: {response}" if response else "✅ LED OFF command sent"
        
        elif intent == "STATUS":
            response = self.serial_controller.get_status()
            return f"📊 Device status: {response}" if response else "📊 Status command sent"
        
        else:
            return "❓ I didn't understand that. Try asking me to turn the LED on/off or check status."
    
    def generate_response(self, user_input, command_result):
        """Generate a natural language response"""
        system_prompt = f"""You are a friendly AI assistant controlling an LED device. 
        
        User said: "{user_input}"
        Command result: "{command_result}"
        
        Respond in a natural, conversational way. Keep it brief and friendly."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate a response"}
        ]
        
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content'].strip()
        except Exception as e:
            return command_result  # Fallback to command result
    
    def chat(self, user_input):
        """Main chat function"""
        # Parse intent
        intent = self.parse_intent(user_input)
        print(f"🎯 Detected intent: {intent}")
        
        # Execute command
        command_result = self.execute_command(intent)
        
        # Generate natural response
        if intent != "UNKNOWN":
            response = self.generate_response(user_input, command_result)
            return response
        else:
            return command_result
    
    def close(self):
        """Close serial connection"""
        if self.serial_controller:
            self.serial_controller.close()

def main():
    print("🤖 Simple AI LED Controller")
    print("=" * 40)
    
    # Get serial port
    port = input("Enter serial port [/dev/cu.usbmodem21102]: ").strip()
    if not port:
        port = "/dev/cu.usbmodem21102"
    
    # Get model name
    model_name = input("Enter Ollama model [gpt-oss:20b]: ").strip()
    if not model_name:
        model_name = "gpt-oss:20b"
    
    # Initialize agent
    agent = SimpleAIAgent(model_name)
    
    if not agent.initialize_serial(port):
        print("Exiting due to serial connection failure.")
        return
    
    print(f"🧠 Using model: {model_name}")
    print("✅ Ready to chat!")
    print("\n💡 Try saying:")
    print("  - 'Please turn on the LED'")
    print("  - 'Turn off the light'")
    print("  - 'What's the device status?'")
    print("  - 'quit' to exit")
    print("-" * 40)
    
    try:
        while True:
            user_input = input("\n🗣️  You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            if not user_input:
                continue
            
            print("🤖 AI: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    finally:
        agent.close()

if __name__ == "__main__":
    main()