from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer()

def ensure_token_passed(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials.scheme != "Bearer" or not credentials.credentials:
        raise HTTPException(
            status_code=401, detail="Invalid or missing access token")
    return credentials.credentials

def get_spotify_client(access_token: str = Depends(ensure_token_passed)):
    return SpotifyClient(access_token)