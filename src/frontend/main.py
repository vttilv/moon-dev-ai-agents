from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime
import shutil

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Moon Dev's RBI Agent 🌙",
    description="Research-Backtest-Implement Trading Strategies with AI",
    version="1.0.0"
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Add src directory to Python path
sys.path.append(str(PROJECT_ROOT / "src"))

# Mount the static directory
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "src/frontend/static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "src/frontend/templates"))

# Required environment variables
required_vars = ["DEEPSEEK_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("❌ Missing required environment variables:", missing_vars)
    print("Please set these in your .env file or Heroku config vars")
    exit(1)

print("✅ All required environment variables found!")

# Use existing data directories in src/data/rbi
data_dir = PROJECT_ROOT / "src/data/rbi"
research_dir = data_dir / "research"
backtests_dir = data_dir / "backtests"
backtests_final_dir = data_dir / "backtests_final"

print(f"📂 Using existing data directory: {data_dir}")

# Global variables for results
processing_results = []
is_processing_complete = False

# Import after setting up Python path
from agents.rbi_agent import process_trading_idea

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/agent/{agent_id}")
async def agent_detail(request: Request, agent_id: str):
    # In a real app, you'd fetch this data from a database
    agent = {
        "name": "Trading Assistant Agent",
        "description": "Your AI-powered trading companion",
        "hero_image": "/static/images/agents/trading-assistant.png",
        "features": [
            {
                "title": "Real-time Analysis",
                "description": "Advanced market analysis in real-time",
                "image": "/static/images/agents/feature1.png"
            },
            # Add more features...
        ]
    }
    return templates.TemplateResponse(
        "agent_detail.html", 
        {"request": request, "agent": agent}
    )

async def process_strategy_background(links: list):
    """Process strategies in the background"""
    global processing_results, is_processing_complete
    
    # Clear old results
    processing_results = []
    is_processing_complete = False
    
    try:
        # Process each strategy
        for i, link in enumerate(links, 1):
            print(f"🌙 Processing Strategy {i}: {link}")
            try:
                # Process the strategy
                process_trading_idea(link)
                
                print("🔍 Looking for output files...")
                print(f"Strategy dir: {research_dir}")
                print(f"Backtest dir: {backtests_final_dir}")
                
                # Get the most recent strategy and backtest files
                strategy_files = list(research_dir.glob("*.txt"))
                backtest_files = list(backtests_final_dir.glob("*.py"))
                
                print(f"Found {len(strategy_files)} strategy files")
                print(f"Found {len(backtest_files)} backtest files")
                
                if strategy_files and backtest_files:
                    strategy_file = max(strategy_files, key=lambda x: x.stat().st_mtime)
                    backtest_file = max(backtest_files, key=lambda x: x.stat().st_mtime)
                    
                    print(f"📄 Reading strategy file: {strategy_file}")
                    print(f"📄 Reading backtest file: {backtest_file}")
                    
                    strategy_content = strategy_file.read_text()
                    backtest_content = backtest_file.read_text()
                    
                    result = {
                        "strategy_number": i,
                        "link": link,
                        "status": "success",
                        "strategy": strategy_content,
                        "backtest": backtest_content,
                        "strategy_file": strategy_file.name,
                        "backtest_file": backtest_file.name
                    }
                    processing_results.append(result)
                    print(f"✅ Strategy {i} complete!")
                else:
                    result = {
                        "strategy_number": i,
                        "link": link,
                        "status": "error",
                        "message": f"Strategy processing completed but output files not found. Strategy files: {len(strategy_files)}, Backtest files: {len(backtest_files)}"
                    }
                    processing_results.append(result)
                    print(f"❌ Strategy {i} failed: Output files not found")
            except Exception as e:
                result = {
                    "strategy_number": i,
                    "link": link,
                    "status": "error",
                    "message": str(e)
                }
                processing_results.append(result)
                print(f"❌ Strategy {i} failed: {str(e)}")
    finally:
        is_processing_complete = True

@app.post("/analyze")
async def analyze_strategy(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    links = form.get("links", "").split("\n")
    links = [link.strip() for link in links if link.strip()]
    
    if not links:
        return JSONResponse({"status": "error", "message": "No links provided"})
    
    # Start processing in background
    background_tasks.add_task(process_strategy_background, links)
    
    return JSONResponse({
        "status": "success",
        "message": "Analysis started"
    })

@app.get("/download/strategy/{filename}")
async def download_strategy(filename: str):
    """Download a strategy file"""
    file_path = research_dir / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/plain"
        )
    return JSONResponse({
        "status": "error",
        "message": "File not found"
    })

@app.get("/download/backtest/{filename}")
async def download_backtest(filename: str):
    """Download a backtest file"""
    file_path = backtests_final_dir / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/plain"
        )
    return JSONResponse({
        "status": "error",
        "message": "File not found"
    })

@app.get("/results")
async def get_results():
    """Get current processing results"""
    return JSONResponse({
        "status": "success",
        "results": processing_results,
        "is_complete": is_processing_complete
    })

@app.get("/request-agent")
async def request_agent_form(request: Request):
    return templates.TemplateResponse("request_agent.html", {"request": request})

@app.get("/submit-agent")
async def submit_agent_form(request: Request):
    return templates.TemplateResponse("submit_agent.html", {"request": request})

@app.get("/thank-you")
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment if available (Heroku), otherwise default to 8000
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 