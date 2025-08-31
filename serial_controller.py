import serial
import time
import sys

class SerialController:
    def __init__(self, port='/dev/cu.usbserial-0001', baudrate=9600, timeout=1):
        """
        Initialize serial connection
        Args:
            port: Serial port (on Mac, typically /dev/cu.usbserial-* or /dev/cu.usbmodem*)
            baudrate: Communication speed
            timeout: Read timeout in seconds
        """
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Wait for connection to establish
            print(f"Connected to {port} at {baudrate} baud")
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
            sys.exit(1)
    
    def send_command(self, command):
        """
        Send command to serial device and return response
        Args:
            command: Command string to send
        Returns:
            Response string from device
        """
        try:
            # Clear input and output buffers
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            
            # Send command with newline
            command_bytes = (command + '\n').encode('utf-8')
            self.serial_port.write(command_bytes)
            print(f"Sent: {command}")
            
            # Wait a bit longer for response
            time.sleep(0.2)
            
            # Read all available responses
            responses = []
            while self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:  # Only add non-empty lines
                    responses.append(line)
                    print(f"Received: {line}")
            
            # Filter responses to get the actual device response
            for response in responses:
                # Skip echo, prompt characters, and empty responses
                if (response.lower() != command.lower() and 
                    response not in ['>', '$', '#'] and  # Common prompt characters
                    len(response) > 1):
                    return response
            
            # If no valid response found, try the delayed read approach
            if len(responses) >= 1 and responses[0].lower() == command.lower():
                time.sleep(0.1)
                if self.serial_port.in_waiting > 0:
                    actual_response = self.serial_port.readline().decode('utf-8').strip()
                    if actual_response and actual_response not in ['>', '$', '#']:
                        print(f"Received (delayed): {actual_response}")
                        return actual_response
        
            return None  # No valid response received
            
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            return None
    
    def led_on(self):
        """Turn LED on and return response"""
        return self.send_command("led on")
    
    def led_off(self):
        """Turn LED off and return response"""
        return self.send_command("led off")
    
    def get_status(self):
        """Get device status and return response"""
        return self.send_command("status")
    
    def close(self):
        """Close serial connection"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial connection closed")