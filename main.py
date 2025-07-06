"""
Main entry point for the Enhanced GitHub Protection Agent
"""
import os
import sys
from github_protection_agent import EnhancedGitHubProtectionAgent, setup_logging
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


def main():
    """Main function to run the agent"""
    config = {
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    }
    
    if not config['USE_LOCAL_MODEL'] and not config['OPENAI_API_KEY']:
        logger.error("❌ Please set OPENAI_API_KEY or USE_LOCAL_MODEL=true")
        return
    
    try:
        agent = EnhancedGitHubProtectionAgent(config)
        
        print("🚀 Enhanced GitHub Protection Agent initialized!")
        print("💬 You can now interact with the agent")
        print("\n📋 Available commands:")
        print("  - analyze <github_url>")
        print("  - register <github_url>")
        print("  - audit <any_url>")
        print("  - clean <text_with_urls>")
        print("  - workflow <github_url>")
        print("  - quit/exit")
        
        while True:
            try:
                user_input = input("\n💬 Ask me anything (or 'quit' to exit): ")
                if user_input.lower() in ['quit', 'exit']:
                    break
                    
                response = agent.agent.run(user_input)
                print(f"\n🤖 Agent: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()