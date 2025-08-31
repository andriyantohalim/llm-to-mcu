import ollama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Any
import json
import re
from serial_controller import SerialController

# Initialize serial controller
serial_controller = None

def initialize_serial(port='/dev/cu.usbmodem21102', baudrate=9600):
    """Initialize the serial controller"""
    global serial_controller
    try:
        serial_controller = SerialController(port=port, baudrate=baudrate)
        print(f"✅ Serial connection established on {port}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize serial connection: {e}")
        return False

@tool
def turn_led_on() -> str:
    """Turn the LED on via serial command"""
    global serial_controller
    if serial_controller is None:
        return "Error: Serial connection not initialized"
    
    response = serial_controller.led_on()
    return f"LED turned ON. Device response: {response}" if response else "LED command sent but no response received"

@tool
def turn_led_off() -> str:
    """Turn the LED off via serial command"""
    global serial_controller
    if serial_controller is None:
        return "Error: Serial connection not initialized"
    
    response = serial_controller.led_off()
    return f"LED turned OFF. Device response: {response}" if response else "LED command sent but no response received"

@tool
def get_device_status() -> str:
    """Get the current status of the device"""
    global serial_controller
    if serial_controller is None:
        return "Error: Serial connection not initialized"
    
    response = serial_controller.get_status()
    return f"Device status: {response}" if response else "Status command sent but no response received"

# Define the state for our agent
class AgentState(TypedDict):
    messages: Annotated[List[Any], "The messages in the conversation"]
    tools_called: Annotated[List[str], "Tools that have been called"]

class AIAgent:
    def __init__(self, model_name="gpt-oss:20b"):
        self.model_name = model_name
        self.tools = {
            "turn_led_on": turn_led_on,
            "turn_led_off": turn_led_off,
            "get_device_status": get_device_status
        }
        
        # Create the graph
        self.workflow = StateGraph(AgentState)
        
        # Add nodes
        self.workflow.add_node("agent", self.call_model)
        self.workflow.add_node("action", self.call_tool)
        
        # Set entry point
        self.workflow.set_entry_point("agent")
        
        # Add edges
        self.workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        self.workflow.add_edge("action", "agent")
        
        # Compile the graph
        self.app = self.workflow.compile()
    
    def should_continue(self, state):
        """Decide whether to continue or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if the last message contains a tool call
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        return "end"
    
    def call_model(self, state):
        """Call the Ollama model"""
        messages = state["messages"]
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                ollama_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                ollama_messages.append({"role": "system", "content": msg.content})
        
        # System prompt for the agent
        system_prompt = {
            "role": "system",
            "content": """You are a helpful AI assistant that can control an LED device through serial commands. 

Available tools:
- turn_led_on(): Turns the LED on
- turn_led_off(): Turns the LED off  
- get_device_status(): Gets the current device status

When users ask you to:
- Turn on/enable/activate the LED -> respond with "TOOL_CALL: turn_led_on"
- Turn off/disable/deactivate the LED -> respond with "TOOL_CALL: turn_led_off"
- Check status/get status -> respond with "TOOL_CALL: get_device_status"

If you need to call a tool, start your response with "TOOL_CALL:" followed by the tool name.
Otherwise, be conversational and helpful in your responses."""
        }
        
        # Add system prompt if not already present
        if not ollama_messages or ollama_messages[0]["role"] != "system":
            ollama_messages.insert(0, system_prompt)
        
        try:
            # Call Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=ollama_messages
            )
            
            content = response['message']['content']
            
            # Check for tool calls in response
            tool_call = self.extract_tool_call(content)
            
            if tool_call:
                ai_message = AIMessage(content=content, tool_calls=[tool_call])
            else:
                ai_message = AIMessage(content=content)
            
            return {"messages": messages + [ai_message]}
            
        except Exception as e:
            error_msg = f"Error calling model: {e}"
            return {"messages": messages + [AIMessage(content=error_msg)]}
    
    def extract_tool_call(self, content):
        """Extract tool call from model response"""
        content_lower = content.lower()
        
        # Check for explicit tool call format
        if "tool_call:" in content_lower:
            if "turn_led_on" in content_lower:
                return {"name": "turn_led_on", "args": {}, "id": "call_led_on"}
            elif "turn_led_off" in content_lower:
                return {"name": "turn_led_off", "args": {}, "id": "call_led_off"}
            elif "get_device_status" in content_lower:
                return {"name": "get_device_status", "args": {}, "id": "call_status"}
        
        # Fallback pattern matching
        if any(phrase in content_lower for phrase in ["turn on", "switch on", "enable", "activate"]) and "led" in content_lower:
            return {"name": "turn_led_on", "args": {}, "id": "call_led_on"}
        elif any(phrase in content_lower for phrase in ["turn off", "switch off", "disable", "deactivate"]) and "led" in content_lower:
            return {"name": "turn_led_off", "args": {}, "id": "call_led_off"}
        elif any(phrase in content_lower for phrase in ["status", "check", "state", "condition"]):
            return {"name": "get_device_status", "args": {}, "id": "call_status"}
        
        return None
    
    def call_tool(self, state):
        """Execute the tool call"""
        messages = state["messages"]
        last_message = messages[-1]
        tools_called = state.get("tools_called", [])
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call["name"]
            
            # Execute the tool
            try:
                if tool_name in self.tools:
                    result = self.tools[tool_name].invoke({})
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Create tool message
                tool_message = AIMessage(content=f"I executed the {tool_name} command. {result}")
                tools_called.append(tool_name)
                
                return {
                    "messages": messages + [tool_message],
                    "tools_called": tools_called
                }
                
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {e}"
                return {
                    "messages": messages + [AIMessage(content=error_msg)],
                    "tools_called": tools_called
                }
        
        return {"messages": messages, "tools_called": tools_called}
    
    def chat(self, user_input):
        """Process user input and return response"""
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "tools_called": []
        }
        
        # Run the workflow
        result = self.app.invoke(initial_state)
        
        # Get the last AI message that's not a tool call
        messages = result["messages"]
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                # Skip tool call messages, return the final response
                if not hasattr(message, 'tool_calls') or not message.tool_calls:
                    return message.content
        
        return "I completed your request!"

def main():
    print("🤖 AI LED Controller Agent")
    print("=" * 50)
    
    # Initialize serial connection
    port = input("Enter serial port [/dev/cu.usbmodem21102]: ").strip()
    if not port:
        port = "/dev/cu.usbmodem21102"
    
    if not initialize_serial(port):
        print("Failed to initialize serial connection. Exiting.")
        return
    
    # Initialize AI agent
    model_name = input("Enter Ollama model [gpt-oss:20b]: ").strip()
    if not model_name:
        model_name = "gpt-oss:20b"
    
    print(f"🧠 Initializing AI agent with model: {model_name}")
    
    try:
        agent = AIAgent(model_name)
        print("✅ AI agent ready!")
        print("\n💡 You can ask me to:")
        print("  - 'Please turn on the LED'")
        print("  - 'Turn off the light'") 
        print("  - 'What's the device status?'")
        print("  - Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            user_input = input("\n🗣️  You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            if not user_input:
                continue
            
            print("🤖 AI: ", end="", flush=True)
            
            try:
                response = agent.chat(user_input)
                print(response)
                
            except Exception as e:
                print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    except Exception as e:
        print(f"Error initializing AI agent: {e}")
    
    finally:
        if serial_controller:
            serial_controller.close()

if __name__ == "__main__":
    main()