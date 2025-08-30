"""
Export/Import API router for crew configurations.
"""
import json
import zipfile
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, validator

from ..database import get_db, Crew, Agent
from ..schemas import CrewResponse

router = APIRouter()


class CrewExportSchema(BaseModel):
    """Schema for crew export data."""
    version: str = "1.0"
    exported_at: str
    crew: Dict[str, Any]
    agents: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class CrewImportRequest(BaseModel):
    """Request model for crew import."""
    crew_data: Dict[str, Any]
    import_as_template: bool = False
    override_name: Optional[str] = None
    
    @validator('crew_data')
    def validate_crew_data(cls, v):
        required_fields = ['version', 'crew', 'agents']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v


@router.get("/{crew_id}/export")
async def export_crew(
    crew_id: int,
    format: str = "json",
    include_metadata: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Export a crew configuration."""
    
    # Get crew
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crew not found"
        )
    
    # Get agents
    agents_result = await db.execute(select(Agent).where(Agent.crew_id == crew_id))
    agents = agents_result.scalars().all()
    
    # Prepare export data
    export_data = CrewExportSchema(
        exported_at=datetime.utcnow().isoformat(),
        crew={
            "name": crew.name,
            "description": crew.description,
            "crew_config": crew.crew_config,
            "roles_config": crew.roles_config,
            "workflows_config": crew.workflows_config,
            "is_template": crew.is_template,
            "is_public": crew.is_public
        },
        agents=[
            {
                "name": agent.name,
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "tools": agent.tools,
                "llm_config": agent.llm_config
            }
            for agent in agents
        ],
        metadata={
            "original_crew_id": crew.id,
            "created_at": crew.created_at.isoformat(),
            "updated_at": crew.updated_at.isoformat(),
            "export_format": format,
            "platform_version": "1.0.0"
        } if include_metadata else {}
    )
    
    if format.lower() == "zip":
        return await _export_as_zip(export_data, crew.name)
    else:
        # Default to JSON
        return await _export_as_json(export_data, crew.name)


async def _export_as_json(export_data: CrewExportSchema, crew_name: str):
    """Export crew as JSON file."""
    json_content = export_data.json(indent=2)
    
    def generate():
        yield json_content.encode('utf-8')
    
    filename = f"{crew_name.replace(' ', '_').lower()}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        generate(),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


async def _export_as_zip(export_data: CrewExportSchema, crew_name: str):
    """Export crew as ZIP file with separate configuration files."""
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Main crew configuration
        zip_file.writestr(
            "crew.json",
            json.dumps(export_data.crew, indent=2)
        )
        
        # Agents configuration
        zip_file.writestr(
            "agents.json",
            json.dumps(export_data.agents, indent=2)
        )
        
        # Individual configuration files
        if export_data.crew.get("crew_config"):
            zip_file.writestr(
                "config/crew_config.json",
                json.dumps(export_data.crew["crew_config"], indent=2)
            )
        
        if export_data.crew.get("roles_config"):
            zip_file.writestr(
                "config/roles_config.json",
                json.dumps(export_data.crew["roles_config"], indent=2)
            )
        
        if export_data.crew.get("workflows_config"):
            zip_file.writestr(
                "config/workflows_config.json",
                json.dumps(export_data.crew["workflows_config"], indent=2)
            )
        
        # Metadata
        if export_data.metadata:
            zip_file.writestr(
                "metadata.json",
                json.dumps(export_data.metadata, indent=2)
            )
        
        # README
        readme_content = f"""# {export_data.crew['name']} - AI Crew Export

## Description
{export_data.crew.get('description', 'No description provided')}

## Export Information
- Exported at: {export_data.exported_at}
- Version: {export_data.version}
- Agents: {len(export_data.agents)}

## Files
- `crew.json` - Main crew configuration
- `agents.json` - Agent definitions
- `config/` - Individual configuration files
- `metadata.json` - Export metadata

## Import Instructions
To import this crew:
1. Use the AI Crew Platform import feature
2. Upload this ZIP file or the individual JSON files
3. Review and customize the configuration as needed
4. Deploy your crew

## Agent Overview
{chr(10).join([f"- {agent['name']}: {agent['role']}" for agent in export_data.agents])}
"""
        zip_file.writestr("README.md", readme_content)
    
    zip_buffer.seek(0)
    
    def generate():
        while True:
            chunk = zip_buffer.read(8192)
            if not chunk:
                break
            yield chunk
    
    filename = f"{crew_name.replace(' ', '_').lower()}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
    
    return StreamingResponse(
        generate(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/import", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def import_crew(
    import_request: CrewImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import a crew configuration."""
    
    crew_data = import_request.crew_data
    
    # Validate version compatibility
    if crew_data.get("version", "1.0") != "1.0":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export version"
        )
    
    # Extract crew information
    crew_info = crew_data["crew"]
    agents_info = crew_data["agents"]
    
    # Override name if provided
    if import_request.override_name:
        crew_info["name"] = import_request.override_name
    
    # Create crew
    crew = Crew(
        name=crew_info["name"],
        description=crew_info.get("description"),
        crew_config=crew_info.get("crew_config"),
        roles_config=crew_info.get("roles_config"),
        workflows_config=crew_info.get("workflows_config"),
        is_template=import_request.import_as_template,
        is_public=crew_info.get("is_public", False),
        organization_id=1,  # TODO: Get from authenticated user
        created_by_id=1,    # TODO: Get from authenticated user
    )
    
    db.add(crew)
    await db.commit()
    await db.refresh(crew)
    
    # Create agents
    for agent_info in agents_info:
        agent = Agent(
            name=agent_info["name"],
            role=agent_info["role"],
            goal=agent_info.get("goal"),
            backstory=agent_info.get("backstory"),
            tools=agent_info.get("tools"),
            llm_config=agent_info.get("llm_config"),
            crew_id=crew.id
        )
        db.add(agent)
    
    await db.commit()
    
    return CrewResponse.from_orm(crew)


@router.post("/import/file", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def import_crew_from_file(
    file: UploadFile = File(...),
    import_as_template: bool = False,
    override_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Import a crew from uploaded file (JSON or ZIP)."""
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_content = await file.read()
    
    try:
        if file.filename.endswith('.zip'):
            crew_data = await _extract_from_zip(file_content)
        elif file.filename.endswith('.json'):
            crew_data = json.loads(file_content.decode('utf-8'))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Use JSON or ZIP files."
            )
        
        # Use the import endpoint
        import_request = CrewImportRequest(
            crew_data=crew_data,
            import_as_template=import_as_template,
            override_name=override_name
        )
        
        return await import_crew(import_request, db)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import crew: {str(e)}"
        )


async def _extract_from_zip(zip_content: bytes) -> Dict[str, Any]:
    """Extract crew data from ZIP file."""
    
    with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
        # Try to read the main export file first
        try:
            # Look for a complete export JSON file
            for filename in zip_file.namelist():
                if filename.endswith('_export.json') or filename == 'export.json':
                    with zip_file.open(filename) as f:
                        return json.loads(f.read().decode('utf-8'))
        except:
            pass
        
        # Otherwise, reconstruct from individual files
        crew_data = {"version": "1.0"}
        
        # Read crew.json
        try:
            with zip_file.open('crew.json') as f:
                crew_data["crew"] = json.loads(f.read().decode('utf-8'))
        except KeyError:
            raise ValueError("Missing crew.json in ZIP file")
        
        # Read agents.json
        try:
            with zip_file.open('agents.json') as f:
                crew_data["agents"] = json.loads(f.read().decode('utf-8'))
        except KeyError:
            raise ValueError("Missing agents.json in ZIP file")
        
        # Read metadata if available
        try:
            with zip_file.open('metadata.json') as f:
                crew_data["metadata"] = json.loads(f.read().decode('utf-8'))
        except KeyError:
            crew_data["metadata"] = {}
        
        return crew_data


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_export_templates(db: AsyncSession = Depends(get_db)):
    """List available crew templates for export."""
    
    result = await db.execute(
        select(Crew).where(Crew.is_template == True).order_by(Crew.name)
    )
    crews = result.scalars().all()
    
    templates = []
    for crew in crews:
        templates.append({
            "id": crew.id,
            "name": crew.name,
            "description": crew.description,
            "created_at": crew.created_at.isoformat(),
            "updated_at": crew.updated_at.isoformat(),
            "export_url": f"/v1/export/{crew.id}/export"
        })
    
    return templates
