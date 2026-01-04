"""
FastAPI endpoints for the Playwright Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from pathlib import Path

from .agent.agent import PlaywrightAgent
from .utils.logger import agent_logger

app = FastAPI(title="Playwright Agent API", version="1.0.0")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (lazy loading)
agent = PlaywrightAgent(
    planner_prompt="planner_v02",
    codegen_prompt="codegen_v02"
)

# Models
class GenerateRequest(BaseModel):
    prompt: str
    project_id: str = "default"

class GenerateResponse(BaseModel):
    success: bool
    task_type: str
    page_object_code: str
    test_code: str
    class_name: str
    saved_files: List[str]
    extracted_locators: Dict[str, str]
    response: str
    duration: float
    iterations: int
    error: Optional[str] = None

class FileReadRequest(BaseModel):
    path: str

class FileWriteRequest(BaseModel):
    path: str
    content: str

class FileListRequest(BaseModel):
    path: str = ""
    project_id: str = "default"


# Endpoints
@app.get("/")
async def root():
    return {"message": "Playwright Agent API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/generate")
async def generate_pom(request: GenerateRequest) -> GenerateResponse:
    """
    Generate Page Object Model using the agent
    """
    agent_logger.info(f"API: Received generate request for project={request.project_id}")
    agent_logger.info(f"API: Prompt: {request.prompt[:100]}...")
    
    try:
        # Call agent
        result = agent.process_request(
            user_prompt=request.prompt,
            project_id=request.project_id
        )
        
        if result["success"]:
            agent_logger.info(f"API: Generation successful - {len(result.get('saved_files', []))} files saved")
            
            return GenerateResponse(
                success=True,
                task_type=result["task_type"],
                page_object_code=result.get("page_object_code", ""),
                test_code=result.get("test_code", ""),
                class_name=result.get("class_name", ""),
                saved_files=result.get("saved_files", []),
                extracted_locators=result.get("extracted_locators", {}),
                response=result.get("response", ""),
                duration=result.get("duration", 0),
                iterations=result.get("iterations", 0)
            )
        else:
            agent_logger.error(f"API: Generation failed - {result.get('error')}", None)
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
    
    except Exception as e:
        agent_logger.error("API: generate_pom", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/list")
async def list_files(path: str = "", project_id: str = "default"):
    """
    List files in workspace
    """
    try:
        workspace_root = Path("workspace") / project_id
        target_path = workspace_root / path if path else workspace_root
        
        if not target_path.exists():
            return {"files": [], "path": path}
        
        files = []
        for item in target_path.iterdir():
            files.append({
                "name": item.name,
                "path": str(item.relative_to(workspace_root)),
                "type": "directory" if item.is_dir() else "file"
            })
        
        return {"files": files, "path": path}
    
    except Exception as e:
        agent_logger.error("API: list_files", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/read")
async def read_file(path: str):
    """
    Read file content
    """
    try:
        file_path = Path("workspace") / path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        content = file_path.read_text(encoding='utf-8')
        return {"content": content, "path": path}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        agent_logger.error("API: read_file", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/write")
async def write_file(request: FileWriteRequest):
    """
    Write file content
    """
    try:
        file_path = Path("workspace") / request.path
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        file_path.write_text(request.content, encoding='utf-8')
        
        agent_logger.info(f"API: File written: {request.path}")
        return {"success": True, "path": request.path}
    
    except Exception as e:
        agent_logger.error("API: write_file", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/delete")
async def delete_file(path: str):
    """
    Delete file
    """
    try:
        file_path = Path("workspace") / path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_path.is_file():
            file_path.unlink()
        else:
            # For directories, use rmdir or shutil.rmtree
            import shutil
            shutil.rmtree(file_path)
        
        agent_logger.info(f"API: File deleted: {path}")
        return {"success": True, "path": path}
    
    except Exception as e:
        agent_logger.error("API: delete_file", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)