"""
Enhanced Main Entry Point for GitHub Protection Agent
With integrated URL cleaning and new command structure
"""
import os
import sys
from github_protection_agent.agent_core_enhanced import EnhancedGitHubProtectionAgent
from github_protection_agent.utils import setup_logging

logger = setup_logging(__name__)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*80)
    print("🛡️  ENHANCED GitHub Repository Protection Agent v4.0")
    print("="*80)
    print("✨ Features:")
    print("   • Automatic URL cleaning on all inputs")
    print("   • Two-repository comparison analysis")
    print("   • Extensive commit history auditing")
    print("   • License PDF generation with IPFS storage")
    print("   • GitHub-wide violation scanning with DMCA generation")
    print("   • Blockchain protection and C2PA metadata support")
    print("="*80 + "\n")


def print_help():
    """Print help information"""
    print("\n📚 Available Commands:")
    print("-" * 60)
    print("analyze <url1> <url2>")
    print("   Compare two GitHub repositories for similarity")
    print("   Example: analyze github.com/user1/repo1 github.com/user2/repo2")
    print()
    print("register <url> [license_type]")
    print("   Register repository with license (default: MIT)")
    print("   License types: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, AGPL-3.0, Custom-AI")
    print("   Example: register https://github.com/user/repo MIT")
    print()
    print("audit <url> [--extensive]")
    print("   Security audit (add --extensive for ALL commits)")
    print("   Example: audit github.com/user/repo --extensive")
    print()
    print("scan [repo_id]")
    print("   Scan GitHub for violations (all registered repos if no ID)")
    print("   Example: scan 1")
    print()
    print("workflow <url>")
    print("   Run complete protection workflow")
    print("   Example: workflow github.com/user/repo")
    print()
    print("list")
    print("   List all registered repositories")
    print()
    print("help")
    print("   Show this help message")
    print()
    print("quit/exit")
    print("   Exit the agent")
    print("-" * 60 + "\n")


def main():
    """Enhanced main function"""
    config = {
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50'),
        'PINATA_API_KEY': os.getenv('PINATA_API_KEY'),
        'PINATA_API_SECRET': os.getenv('PINATA_API_SECRET'),
        'WEB3_STORAGE_TOKEN': os.getenv('WEB3_STORAGE_TOKEN')
    }
    
    if not config['USE_LOCAL_MODEL'] and not config['OPENAI_API_KEY']:
        logger.error("❌ Please set OPENAI_API_KEY or USE_LOCAL_MODEL=true")
        return
    
    try:
        agent = EnhancedGitHubProtectionAgent(config)
        print_banner()
        print_help()
        
        while True:
            try:
                user_input = input("🤖 Agent> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    print_help()
                
                elif command == 'analyze':
                    if len(parts) < 3:
                        print("❌ Usage: analyze <url1> <url2>")
                        continue
                    
                    print("🔍 Analyzing repositories...")
                    result = agent.analyze_repositories(parts[1], parts[2])
                    
                    if result['success']:
                        print(f"\n✅ Analysis Complete")
                        print(f"📊 Overall Similarity: {result['similarity_analysis']['overall_similarity']:.2%}")
                        print(f"🔗 {result['recommendation']}")
                        
                        if result['registered_matches']:
                            print(f"\n⚠️ Found {len(result['registered_matches'])} registered repositories with similarities!")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'register':
                    if len(parts) < 2:
                        print("❌ Usage: register <url> [license_type]")
                        continue
                    
                    license_type = parts[2] if len(parts) > 2 else "MIT"
                    print(f"📝 Registering repository with {license_type} license...")
                    
                    result = agent.register_repository(parts[1], license_type)
                    
                    if result['success']:
                        print(f"\n✅ Repository Registered!")
                        print(f"📋 Repo ID: {result['repo_id']}")
                        print(f"🔗 Transaction: {result['tx_hash'][:16]}...")
                        print(f"📄 License PDF: {result['license']['pdf_path']}")
                        print(f"🌐 IPFS URL: {result['license']['ipfs_url']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'audit':
                    if len(parts) < 2:
                        print("❌ Usage: audit <url> [--extensive]")
                        continue
                    
                    extensive = '--extensive' in parts
                    mode = "EXTENSIVE (all commits)" if extensive else "standard"
                    print(f"🔒 Running {mode} security audit...")
                    
                    result = agent.comprehensive_audit(parts[1], include_all_commits=extensive)
                    
                    if result['success']:
                        print(f"\n✅ Audit Complete")
                        print(f"📁 Files scanned: {result['files_scanned']}")
                        print(f"📊 Commits scanned: {result.get('commits_scanned', 'N/A')}")
                        print(f"🚨 Total findings: {result['total_findings']}")
                        print(f"   Critical: {result['critical_findings']}")
                        print(f"   High: {result['high_findings']}")
                        print(f"   Medium: {result['medium_findings']}")
                        print(f"   Low: {result['low_findings']}")
                        
                        if result.get('report'):
                            print(f"\n📄 Report: {result['report']['ipfs_url']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'scan':
                    repo_id = int(parts[1]) if len(parts) > 1 else None
                    target = f"repository {repo_id}" if repo_id else "all registered repositories"
                    print(f"🔎 Scanning GitHub for violations of {target}...")
                    
                    result = agent.scan_github_for_violations(repo_id)
                    
                    if result['success']:
                        print(f"\n✅ Scan Complete")
                        print(f"📊 Repositories scanned: {result['repositories_scanned']}")
                        print(f"⚠️ Violations found: {result['violations_found']}")
                        print(f"📄 DMCA notices generated: {result['dmca_notices_generated']}")
                        
                        for notice in result['dmca_notices']:
                            print(f"\n🚨 DMCA Notice #{notice['id']}:")
                            print(f"   Infringing URL: {notice['infringing_url']}")
                            print(f"   Similarity: {notice['similarity_score']:.2%}")
                            print(f"   IPFS: {notice['ipfs_url']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'workflow':
                    if len(parts) < 2:
                        print("❌ Usage: workflow <url>")
                        continue
                    
                    print("🚀 Running complete protection workflow...")
                    result = agent.run_protection_workflow(parts[1])
                    
                    if result.get('success'):
                        print(f"\n✅ Workflow Complete!")
                        summary = result['summary']
                        print(f"📋 Repo ID: {summary['repo_id']}")
                        print(f"🔒 Security findings: {summary['security_findings']}")
                        print(f"⚠️ Violations found: {summary['violations_found']}")
                        print(f"✅ Protection active: {summary['protection_active']}")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                elif command == 'list':
                    if not agent.repositories:
                        print("📭 No repositories registered yet")
                    else:
                        print(f"\n📚 Registered Repositories ({len(agent.repositories)}):")
                        print("-" * 60)
                        for repo_id, repo_data in agent.repositories.items():
                            print(f"ID: {repo_id}")
                            print(f"   URL: {repo_data['github_url']}")
                            print(f"   License: {repo_data['license_type']}")
                            print(f"   Registered: {repo_data['registered_at'][:10]}")
                            print()
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"❌ An error occurred: {e}")
                
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()