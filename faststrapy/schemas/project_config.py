from pydantic import BaseModel


class PreConfig(BaseModel):
    project_name: str 
    framework: str 
    python_version: float
    default_settings: bool
    holder_folder: str
    

class DefaultConfig(BaseModel):
    use_pydantic: bool = False
    use_orm: bool = False
    orm_name: str | None = None # sqlalchemy, djangoorm
    use_database: bool = False
    database_name: str | None = None # postgres, sqlite3
    database_type: str | None = None # sync, async
    database_host: str | None = None # neon, pgadmin
    env_prefix: str | None = None 
    use_alembic: bool = False
    alembic_type: str | None = None # sync, async
    use_logs: bool = False
    save_logs_db: bool = False # saves to file
    use_black: bool = False # formatting
    use_docker: bool = False # Dockerfile + docker-compose.yml
    path_name: str
    

class ProjectConfigSchema(BaseModel):
    """Project Configuration Schema"""
    
    pre_config: PreConfig
    default_config: DefaultConfig
