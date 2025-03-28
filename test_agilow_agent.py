#!/usr/bin/env python3
"""
Test script for the Agilow Agent
"""

import os
import sys
from utils.config_manager import ConfigManager
from agents.agilow_agent import AgilowAgent

def main():
    """Main test function"""
    print("\n" + "=" * 50)
    print("Agilow Agent Test")
    print("=" * 50 + "\n")
    
    # Initialize config manager
    try:
        config = ConfigManager()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please check your .env file.")
        sys.exit(1)
    
    # Initialize the Agilow agent
    agent = AgilowAgent()
    
    # Print the greeting
    greeting = agent.generate_greeting()
    print(f"🤖 Agilow: {greeting}\n")
    
    # Test conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nExiting test script. Goodbye!")
            break
        
        # Process the input
        response = agent.process_input(user_input)
        
        # Print the response
        print(f"\n🤖 Agilow: {response['message']}\n")
        
        # Print actions if any
        if response["actions"]:
            print("Actions:")
            for i, action in enumerate(response["actions"], 1):
                print(f"  {i}. {action['type']} - {action['operation'] if 'operation' in action else 'create'}")
        
        # Check if we should exit
        if response["should_exit"]:
            print("\nAgilow has indicated the conversation should end. Goodbye!")
            break

if __name__ == "__main__":
    main() 