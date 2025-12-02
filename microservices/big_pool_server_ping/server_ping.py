from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Check(BaseModel):
    ip: str
    port: int
    endpoint: str

def servercheck(ip, port, endpoint):
    endpoint = endpoint.lstrip("/")
    if endpoint:
        url = f"http://{ip}:{port}/{endpoint}"
    else:
        url = f"http://{ip}:{port}/"

    try:
        requests.get(url, timeout=2)
        return True
    except Exception:
        return False

@app.post("/check")
async def checkendpoint(data: Check):
    result = servercheck(data.ip, data.port, data.endpoint)
    return result