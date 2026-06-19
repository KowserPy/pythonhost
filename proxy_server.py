from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import uvicorn
from typing import Optional, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProxyRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    proxy: Optional[str] = None

@app.post("/api/proxy")
def proxy_request(req: ProxyRequest):
    proxies = None
    if req.proxy:
        # Expected format: host:port:user:pass
        parts = req.proxy.split(":")
        if len(parts) == 4:
            host, port, user, pwd = parts
            proxy_url = f"http://{user}:{pwd}@{host}:{port}"
        elif len(parts) == 2:
            host, port = parts
            proxy_url = f"http://{host}:{port}"
        else:
            proxy_url = f"http://{req.proxy}"
        
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

    try:
        response = requests.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            json=req.body,
            proxies=proxies,
            timeout=30
        )
        return {
            "status": response.status_code,
            "ok": response.ok,
            "text": response.text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("proxy_server:app", host="127.0.0.1", port=8000, reload=True)
