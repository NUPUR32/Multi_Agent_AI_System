#!/usr/bin/env python3
"""
===========================================================
|  NUPUR32® AI OPERATING SYSTEM                          |
|  Autonomous • Self-Improving • Enterprise-Grade        |
|  Version: 2035.0.0 (Codename: NOVA)                    |
|                                                        |
|  "An AI Company Inside Your Computer"                  |
===========================================================

This is the main entry point for the NUPUR32 AI Ecosystem.
A fully autonomous, self-improving, production-ready AI Operating System
capable of replacing entire software teams.

Usage:
    python main.py                          # Interactive mode
    python main.py --mission "your task"    # CLI mission mode
    python main.py --dashboard              # Launch futuristic dashboard
    python main.py --status                 # System status
    python main.py --init                   # Initialize/start system
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_ecosystem import __version__, __codename__
from ai_ecosystem.orchestrator import orchestrator, AIOrchestrator
from ai_ecosystem.monitoring.monitor import global_system_monitor
from ai_ecosystem.config.settings import get_settings

logger = logging.getLogger(__name__)


def print_banner():
    """Print the system banner"""
    banner = f"""
    +--------------------------------------------------------------+
    |                                                              |
    |     NUPUR32 AI OPERATING SYSTEM                              |
    |     Version {__version__:>8}  -  Codename: {__codename__}                |
    |     "An AI Company Inside Your Computer"                     |
    |                                                              |
    +--------------------------------------------------------------+
    """
    print(banner)
    print(f"    System initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    {40} agents ready")
    print(f"    {10} reasoning frameworks")
    print(f"    {14} memory types")
    print(f"    {3} knowledge systems (RAG + Graph + Vector)")
    print("=" * 62)


async def init_system():
    """Initialize the complete AI ecosystem"""
    print_banner()
    print("\n🚀 Initializing NUPUR32 AI Ecosystem...")
    
    await orchestrator.initialize()
    
    status = await orchestrator.get_system_status()
    print(f"\n✅ System initialized successfully!")
    print(f"   • Agents: {status['agents']['total']} operational")
    print(f"   • Memory: {status['memory']['total_entries']} entries")
    print(f"   • Models: registered and ready")
    print(f"   • Status: {status['status']}")
    
    return orchestrator


async def run_mission(objective: str):
    """Run a mission with a specific objective"""
    if not orchestrator.running:
        await init_system()
    
    print(f"\n🎯 Mission: {objective}")
    print("=" * 62)
    
    result = await orchestrator.run_mission(objective)
    
    print(f"\n🏁 Mission Status: {result['status'].upper()}")
    print(f"   • Mission ID: {result['mission_id']}")
    print(f"   • Phases Completed: {len(result['phases'])}")
    print(f"   • Final Output: {result.get('final_output', 'N/A')[:200]}")
    
    return result


async def show_status():
    """Display comprehensive system status"""
    try:
        status = await orchestrator.get_system_status()
        print(json.dumps(status, indent=2, default=str))
    except Exception as e:
        print(f"System not initialized. Run with --init first. ({e})")


async def main_async():
    """Async main entry point"""
    parser = argparse.ArgumentParser(
        description="NUPUR32 AI Operating System - Autonomous AI Ecosystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                       # Interactive mode
  python main.py --init                # Initialize system
  python main.py --mission "Analyze trends in AI"  # Run mission
  python main.py --dashboard           # Launch futuristic dashboard
  python main.py --status              # Show system status
  python main.py --version             # Show version
        """
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize the AI ecosystem")
    parser.add_argument("--mission", type=str, help="Run a mission with objective")
    parser.add_argument("--dashboard", action="store_true", help="Launch the NOVA Control Center Dashboard")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--api", action="store_true", help="Start REST API server")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"NUPUR32 AI OS v{__version__} ({__codename__})")
        print(f"Build: {__version__}.{__build__}" if hasattr(__import__('ai_ecosystem'), '__build__') else "")
        return
    
    if args.init:
        await init_system()
        return
    
    if args.mission:
        await run_mission(args.mission)
        return
    
    if args.dashboard:
        print("🚀 Launching NUPUR32 Control Center...")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard_nova.py", "--", "--live"],
                          check=True)
        except FileNotFoundError:
            print("Streamlit not found. Install with: pip install streamlit")
        except Exception as e:
            print(f"Failed to launch dashboard: {e}")
        return
    
    if args.api:
        print("🚀 Starting REST API server...")
        try:
            import uvicorn
            uvicorn.run("ai_ecosystem.api:app", host="0.0.0.0", port=8000, reload=True)
        except ImportError:
            print("FastAPI/uvicorn not found. Install with: pip install fastapi uvicorn")
        return
    
    if args.status:
        await show_status()
        return
    
    # Default: Interactive mode
    print_banner()
    print("\nNUPUR32 AI Operating System - Interactive Mode")
    print("=" * 62)
    
    await init_system()
    
    while True:
        print("\n" + "=" * 62)
        print("1. 🎯 Run Mission")
        print("2. 📊 System Status")
        print("3. 🖥️ Launch Dashboard")
        print("4. 🔄 Run Health Check")
        print("5. ❌ Shutdown")
        print("=" * 62)
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                objective = input("Enter mission objective: ")
                await run_mission(objective)
            
            elif choice == "2":
                await show_status()
            
            elif choice == "3":
                print("Launching Control Center...")
                import subprocess
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard_nova.py", "--", "--live"])
            
            elif choice == "4":
                results = global_system_monitor.run_health_checks()
                for r in results:
                    status_icon = "✅" if r["healthy"] else "❌"
                    status_msg = "Healthy" if r["healthy"] else f"Failed - {r.get('error', '')}"
                    print(f"  {status_icon} {r['name']}: {status_msg}")
            
            elif choice == "5":
                print("\nShutting down NUPUR32 AI OS...")
                await orchestrator.shutdown()
                print("Goodbye! 👋")
                break
            
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            await orchestrator.shutdown()
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Synchronous entry point"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()