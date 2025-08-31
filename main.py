import time
from serial_controller import SerialController

def main():
    # You may need to change this port based on your system
    # Use 'ls /dev/cu.*' in terminal to see available ports on Mac
    controller = SerialController(port='/dev/cu.usbmodem21102', baudrate=9600)
    
    try:
        # Test LED commands
        print("\n--- Testing LED Control ---")
        
        # Turn LED on
        response = controller.led_on()
        if response:
            print(f"LED ON response: {response}")
        
        time.sleep(1)
        
        # Turn LED off
        response = controller.led_off()
        if response:
            print(f"LED OFF response: {response}")
        
        time.sleep(1)
        
        # Get status
        print("\n--- Getting Status ---")
        response = controller.get_status()
        if response:
            print(f"Status response: {response}")
        
        # Interactive mode
        print("\n--- Interactive Mode ---")
        print("Available commands: 'led on', 'led off', 'status', 'quit'")
        
        while True:
            user_input = input("\nEnter command: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'led on':
                response = controller.led_on()
            elif user_input.lower() == 'led off':
                response = controller.led_off()
            elif user_input.lower() == 'status':
                response = controller.get_status()
            else:
                print("Invalid command. Use 'led on', 'led off', 'status', or 'quit'")
                continue
            
            if response:
                print(f"Response: {response}")
            else:
                print("No response or error occurred")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        controller.close()

if __name__ == "__main__":
    main()