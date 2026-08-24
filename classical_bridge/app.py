from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys

# Ensure q_engine and other modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classical_bridge.processing_worker import run_simulation_task, WorkerConfig

app = FastAPI(title="QDMS Unified Application", description="Unified Simulator and Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationConfig(BaseModel):
    num_assets: int = 4
    shock_intensity: float = 0.5
    time_steps: int = 50

@app.post("/api/simulate")
def run_simulation(config: SimulationConfig):
    """
    Triggers a new market collapse simulation run using the quantum engine.
    """
    try:
        worker_config = WorkerConfig(
            num_assets=config.num_assets,
            shock_intensity=config.shock_intensity,
            time_steps=config.time_steps
        )
        result = run_simulation_task(worker_config)
        return {
            "status": "Simulation completed",
            "config": config.model_dump(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@app.get("/api/status")
async def get_status():
    """
    Checks if the backend is alive.
    """
    return {"status": "alive"}

# Serve the static files from dashboard/dist
dashboard_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "dist")

if os.path.exists(dashboard_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(dashboard_dist, "assets")), name="assets")
    app.mount("/vite.svg", StaticFiles(directory=dashboard_dist, html=True), name="vite")
    
    @app.get("/{full_path:path}")
    async def serve_dashboard(full_path: str):
        index_path = os.path.join(dashboard_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Dashboard not built"}
else:
    @app.get("/")
    async def fallback():
        return {"error": "Dashboard not built. Please run 'npm run build' in the dashboard directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
