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
            
        # Ensure no orphaned processes are running before we start
        try:
            subprocess.run(["pkill", "-f", "tag_simulator.py"], capture_output=True)
        except Exception as e:
            logger.debug(f"pkill check failed or not available: {e}")
        
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
        killed_any = False
        
        if _simulator_process is not None:
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
                killed_any = True
            except Exception as e:
                logger.error(f"Error stopping tracked simulator: {e}")
            finally:
                _simulator_process = None
                
        # Catch any orphaned processes (e.g. after a hot reload)
        try:
            result = subprocess.run(["pkill", "-f", "tag_simulator.py"], capture_output=True)
            if result.returncode == 0:
                logger.info("Killed orphaned tag_simulator.py processes via pkill.")
                killed_any = True
        except Exception as e:
            logger.debug(f"pkill failed or not available: {e}")
            
        # Always return success so the frontend UI state can sync back to "Start Simulator"
        return {
            "status": "success",
            "message": "Tag simulator stopped (or was already stopped)",
            "killed_processes": killed_any
        }


@router.get("/status")
async def simulator_status() -> Dict[str, Any]:
    """
    Check if the simulator is currently running across any worker.
    
    Returns:
        Status response with running state and PID if applicable
    """
    try:
        # Use pgrep to check for the process across the entire OS (multi-worker safe)
        result = subprocess.run(["pgrep", "-f", "tag_simulator.py"], capture_output=True, text=True)
        is_running = result.returncode == 0
        
        pid = None
        if is_running and result.stdout.strip():
            # Get the first PID found
            pid_str = result.stdout.strip().split('\n')[0]
            try:
                pid = int(pid_str)
            except ValueError:
                pass
                
        return {
            "status": "success",
            "is_running": is_running,
            "pid": pid
        }
    except Exception as e:
        logger.error(f"Error checking simulator status: {e}")
        # Fallback to local memory if pgrep fails
        global _simulator_process
        with _simulator_lock:
            is_running = _simulator_process is not None and _simulator_process.poll() is None
            return {
                "status": "success",
                "is_running": is_running,
                "pid": _simulator_process.pid if is_running else None
            }
