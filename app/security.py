from fastapi import Header, HTTPException, status

from app.config import settings

async def verify_api_key(x_api_key: str | None = Header(default=None)):
    """API access is protected using an `X-API-Key` header, while the `/health` 
    endpoint remains public so monitoring systems can check the API status without 
    authentication.
    """
    
    if x_api_key is None or x_api_key != settings.API_KEY:
        
        raise HTTPException(
            
            status_code=status.HTTP_401_UNAUTHORIZED,
            
            detail="Invalid or missing API key",
        ) 