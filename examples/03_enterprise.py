#!/usr/bin/env python3
"""
Enterprise Workflows Example

This example demonstrates enterprise-grade usage patterns for the Letta MCP Server,
including team-based agent management, security considerations, and workflow automation
across multiple AI clients.

Features:
- Team-based agent templates
- Role-based access patterns
- Multi-client deployment strategies
- Monitoring and analytics
- Enterprise security practices
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# Note: In real enterprise usage, you'd import the actual Letta client
# from letta_client import Letta

class EnterpriseAgentManager:
    """Enterprise-grade agent management with MCP integration"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.letta.com"):
        self.api_key = api_key
        self.base_url = base_url
        # self.client = Letta(token=api_key, base_url=base_url)
        
    async def setup_team_agents(self, team_config: Dict) -> List[str]:
        """Setup standardized agents for a development team"""
        agent_ids = []
        
        for role, config in team_config.items():
            print(f"🤖 Creating {role} agent...")
            
            # In real implementation:
            # agent = await self.client.agents.create(
            #     name=f"{team_config['team_name']}-{role}",
            #     persona=config['persona'],
            #     tools=config['tools'],
            #     memory=config.get('initial_memory', {})
            # )
            # agent_ids.append(agent.id)
            
            # For demo:
            mock_agent_id = f"agent-{role}-{datetime.now().strftime('%Y%m%d')}"
            agent_ids.append(mock_agent_id)
            print(f"✅ Created {role} agent: {mock_agent_id}")
            
        return agent_ids

def create_team_configuration() -> Dict:
    """Create standardized team agent configuration"""
    return {
        "team_name": "product-engineering",
        "lead_developer": {
            "persona": """You are a senior lead developer with expertise in:
            - System architecture and design patterns
            - Code review and quality standards
            - Team coordination and technical leadership
            - Performance optimization and scalability
            
            Always consider: security, maintainability, team knowledge sharing.""",
            "tools": ["web_search", "code_analysis", "documentation_search"],
            "initial_memory": {
                "human": "Lead developer for product engineering team",
                "team_standards": "Follows company coding standards and security policies"
            }
        },
        "backend_specialist": {
            "persona": """You are a backend systems specialist focused on:
            - API design and microservices architecture
            - Database optimization and data modeling
            - Security and authentication systems
            - DevOps and deployment automation
            
            Always prioritize: scalability, security, monitoring, documentation.""",
            "tools": ["api_testing", "database_query", "deployment_tools"],
            "initial_memory": {
                "human": "Backend specialist handling API and infrastructure",
                "tech_stack": "Python, PostgreSQL, Docker, Kubernetes"
            }
        },
        "frontend_specialist": {
            "persona": """You are a frontend development specialist expert in:
            - Modern JavaScript frameworks (React, Vue, Angular)
            - UI/UX best practices and accessibility
            - Performance optimization and bundling
            - Cross-browser compatibility and testing
            
            Always consider: user experience, accessibility, performance, maintainability.""",
            "tools": ["ui_testing", "performance_analysis", "design_systems"],
            "initial_memory": {
                "human": "Frontend specialist handling user interfaces",
                "frameworks": "React, TypeScript, Tailwind CSS, Vite"
            }
        },
        "qa_engineer": {
            "persona": """You are a quality assurance engineer specializing in:
            - Test strategy and automation
            - Bug triage and regression testing
            - Performance and security testing
            - CI/CD pipeline quality gates
            
            Always focus on: comprehensive testing, risk assessment, quality metrics.""",
            "tools": ["test_automation", "bug_tracking", "performance_monitoring"],
            "initial_memory": {
                "human": "QA engineer ensuring product quality",
                "testing_approach": "Automated testing with manual exploratory validation"
            }
        }
    }

class MultiClientDeployment:
    """Manage MCP server deployment across multiple AI clients"""
    
    @staticmethod
    def generate_client_configs() -> Dict[str, Dict]:
        """Generate client-specific configurations for enterprise deployment"""
        
        base_server_config = {
            "command": "letta-mcp",
            "args": ["run"],
            "env": {
                "LETTA_API_KEY": "${LETTA_API_KEY}",
                "LETTA_BASE_URL": "${LETTA_BASE_URL:-https://api.letta.com}",
                "LETTA_TIMEOUT": "60",
                "LETTA_MAX_RETRIES": "3",
                "LETTA_LOG_LEVEL": "INFO"
            }
        }
        
        return {
            "claude_desktop": {
                "file_path": "~/.config/claude/claude_desktop_config.json",
                "config": {
                    "mcpServers": {
                        "letta": base_server_config
                    }
                }
            },
            "vscode_copilot": {
                "file_path": ".vscode/settings.json",
                "config": {
                    "chat.mcp.enabled": True,
                    "chat.mcp.servers": {
                        "letta": base_server_config
                    }
                }
            },
            "cursor": {
                "file_path": "cursor-mcp-config.json",
                "config": {
                    "mcp_servers": [
                        {
                            "name": "letta",
                            **base_server_config
                        }
                    ]
                }
            }
        }

class EnterpriseWorkflows:
    """Enterprise workflow patterns using Letta agents via MCP"""
    
    @staticmethod
    def code_review_workflow():
        """Code review workflow using multiple agents"""
        return {
            "name": "Enterprise Code Review",
            "description": "Multi-agent code review process",
            "steps": [
                {
                    "client": "github_copilot",
                    "action": "Initial code analysis",
                    "agent": "lead_developer",
                    "prompt": "Review this pull request for architectural concerns and coding standards"
                },
                {
                    "client": "cursor",
                    "action": "Security review",
                    "agent": "backend_specialist", 
                    "prompt": "Analyze this code for security vulnerabilities and data handling issues"
                },
                {
                    "client": "claude_desktop",
                    "action": "Documentation review",
                    "agent": "qa_engineer",
                    "prompt": "Check if this code change requires documentation updates and test coverage"
                }
            ]
        }
    
    @staticmethod
    def incident_response_workflow():
        """Incident response workflow across multiple platforms"""
        return {
            "name": "Production Incident Response",
            "description": "Coordinated incident response using multiple AI clients",
            "steps": [
                {
                    "client": "claude_desktop",
                    "action": "Initial triage",
                    "agent": "lead_developer",
                    "prompt": "Analyze this production alert and suggest immediate investigation steps"
                },
                {
                    "client": "vscode_copilot",
                    "action": "Code investigation",
                    "agent": "backend_specialist",
                    "prompt": "Review recent deployments and identify potential root causes"
                },
                {
                    "client": "replit",
                    "action": "Hotfix development",
                    "agent": "backend_specialist",
                    "prompt": "Create minimal viable hotfix for this production issue"
                }
            ]
        }

def setup_enterprise_monitoring():
    """Setup monitoring and analytics for enterprise usage"""
    monitoring_config = {
        "metrics": {
            "agent_usage": "Track agent interactions across all clients",
            "response_times": "Monitor MCP server performance",
            "error_rates": "Alert on API failures or timeouts",
            "client_distribution": "Track which clients are most used"
        },
        "alerts": {
            "high_error_rate": "Alert when error rate > 5%",
            "slow_responses": "Alert when avg response > 10s",
            "agent_downtime": "Alert when agents are unreachable"
        },
        "reporting": {
            "daily_usage": "Summary of agent interactions",
            "performance_trends": "Week-over-week performance analysis",
            "cost_tracking": "API usage and cost attribution by team"
        }
    }
    
    print("📊 Enterprise Monitoring Configuration:")
    print(json.dumps(monitoring_config, indent=2))
    return monitoring_config

def security_best_practices():
    """Enterprise security recommendations"""
    practices = {
        "api_key_management": [
            "Use environment variables, never hardcode keys",
            "Rotate API keys quarterly",
            "Use different keys for dev/staging/prod",
            "Monitor API key usage and access patterns"
        ],
        "network_security": [
            "Use VPN or private networks for sensitive data",
            "Implement rate limiting and request validation",
            "Log all API interactions for audit trails",
            "Use HTTPS for all communications"
        ],
        "data_governance": [
            "Classify data sensitivity levels",
            "Implement data retention policies",
            "Ensure compliance with GDPR/CCPA",
            "Regular security audits and penetration testing"
        ],
        "access_control": [
            "Role-based agent access",
            "Team-specific agent configurations",
            "Audit logs for all agent interactions",
            "Principle of least privilege"
        ]
    }
    
    print("🔒 Enterprise Security Best Practices:")
    for category, items in practices.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")
    
    return practices

async def main():
    """Run enterprise setup demonstration"""
    print("🏢 Letta MCP Server - Enterprise Workflows")
    print("=" * 60)
    print("This example demonstrates enterprise-grade usage patterns")
    print("for the Letta MCP Server across multiple AI clients.\n")
    
    # Setup team configuration
    print("👥 Setting up team agents...")
    team_config = create_team_configuration()
    
    manager = EnterpriseAgentManager(
        api_key=os.getenv('LETTA_API_KEY', 'demo-key'),
        base_url=os.getenv('LETTA_BASE_URL', 'https://api.letta.com')
    )
    
    agent_ids = await manager.setup_team_agents(team_config)
    print(f"✅ Created {len(agent_ids)} team agents\n")
    
    # Multi-client deployment
    print("🌐 Generating multi-client configurations...")
    deployment = MultiClientDeployment()
    client_configs = deployment.generate_client_configs()
    
    for client_name, config in client_configs.items():
        print(f"📁 {client_name}: {config['file_path']}")
    print()
    
    # Workflow examples
    print("🔄 Enterprise workflow examples:")
    workflows = EnterpriseWorkflows()
    
    code_review = workflows.code_review_workflow()
    print(f"• {code_review['name']}: {len(code_review['steps'])} steps")
    
    incident = workflows.incident_response_workflow()
    print(f"• {incident['name']}: {len(incident['steps'])} steps")
    print()
    
    # Monitoring setup
    setup_enterprise_monitoring()
    print()
    
    # Security practices
    security_best_practices()
    
    print("\n🎉 Enterprise setup demonstration complete!")
    print("\nKey benefits for enterprise usage:")
    print("• Standardized agents across all AI clients")
    print("• Role-based access and team configurations")
    print("• Comprehensive monitoring and security")
    print("• Workflow automation across platforms")
    print("• Future-proof MCP standard compliance")

if __name__ == "__main__":
    asyncio.run(main())