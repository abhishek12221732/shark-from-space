"""
Simulator control endpoints.

Manages the tag simulator process (start/stop).
"""

import logging
import subprocess
import threading
import sys
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()

# Global simulator process management
_simulator_process: subprocess.Popen = None
_simulator_lock = threading.Lock()


@router.post("/start")
async def start_simulator() -> Dict[str, Any]:
    """
    Start the tag simulator process.
    
    Returns:
        Success response with simulator status
        
    Raises:
        HTTPException: If simulator is already running or fails to start
    """
    global _simulator_process
    
    with _simulator_lock:
        if _simulator_process is not None and _simulator_process.poll() is None:
            raise HTTPException(
                status_code=400,
                detail="Simulator is already running"
            )
        
        try:
            # Navigate from: app/api/endpoints/simulator.py -> backend directory
            backend_dir = Path(__file__).resolve().parent.parent.parent.parent
            simulator_script = backend_dir / "scripts" / "tag_simulator.py"
            
            if not simulator_script.exists():
                raise FileNotFoundError(f"Simulator script not found: {simulator_script}")
            
            # Use the same Python executable as the current process
            python_executable = sys.executable
            
            # Prepare environment - copy parent environment to inherit .env variables
            env = os.environ.copy()
            
            # Start the simulator process with proper environment
            # Use None for stdout/stderr to let it output to console, or DEVNULL to suppress
            _simulator_process = subprocess.Popen(
                [python_executable, str(simulator_script)],
                cwd=str(backend_dir),
                env=env,
                stdout=None,  # Let output go to console
                stderr=None   # Let errors go to console
            )
            
            logger.info(f"Started tag simulator (PID: {_simulator_process.pid})")
            logger.info(f"Script: {simulator_script}")
            logger.info(f"Working dir: {backend_dir}")
            logger.info(f"Python: {python_executable}")
            
            return {
                "status": "success",
                "message": "Tag simulator started",
                "pid": _simulator_process.pid
            }
            
        except FileNotFoundError as e:
            logger.error(f"Simulator script not found: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Simulator script not found: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to start simulator: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start simulator: {str(e)}"
            )


@router.post("/stop")
async def stop_simulator() -> Dict[str, Any]:
    """
    Stop the running tag simulator process.
    
    Returns:
        Success response with termination status
        
    Raises:
        HTTPException: If no simulator is running or termination fails
    """
    global _simulator_process
    
    with _simulator_lock:
        if _simulator_process is None:
            raise HTTPException(
                status_code=400,
                detail="No simulator is currently running"
            )
        
        try:
            # Terminate the process gracefully
            _simulator_process.terminate()
            
            try:
                _simulator_process.wait(timeout=5)
                logger.info(f"Simulator process terminated (PID: {_simulator_process.pid})")
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination times out
                _simulator_process.kill()
                _simulator_process.wait()
                logger.warning(f"Simulator process force-killed (PID: {_simulator_process.pid})")
            
            _simulator_process = None
            
            return {
                "status": "success",
                "message": "Tag simulator stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop simulator: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop simulator: {str(e)}"
            )


@router.get("/status")
async def simulator_status() -> Dict[str, Any]:
    """
    Check if the simulator is currently running.
    
    Returns:
        Status response with running state and PID if applicable
    """
    global _simulator_process
    
    with _simulator_lock:
        is_running = _simulator_process is not None and _simulator_process.poll() is None
        
        return {
            "status": "success",
            "is_running": is_running,
            "pid": _simulator_process.pid if is_running else None
        }
