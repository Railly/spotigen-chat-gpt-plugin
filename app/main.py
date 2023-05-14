from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import yaml

app = FastAPI()

origins = [
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.post("/todos/{username}")
async def add_todo(username: str, request: Request):
    data = await request.json()
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(data["todo"])
    return JSONResponse(content='OK', status_code=200)

@app.get("/todos/{username}")
async def get_todos(username: str):
    return JSONResponse(content=_TODOS.get(username, []), status_code=200)

@app.delete("/todos/{username}")
async def delete_todo(username: str, request: Request):
    data = await request.json()
    todo_idx = data["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return JSONResponse(content='OK', status_code=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return JSONResponse(content=text, status_code=200)

@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return PlainTextResponse(text, media_type="text/yaml")

@app.get("/")
async def root():
    return PlainTextResponse("Hello World!")

@app.get("/generate-openapi-yaml")
def generate_openapi_yaml():
    openapi_dict = app.openapi()
    with open("openapi.yaml", "w") as file:
        yaml.dump(openapi_dict, file)
    return {"detail": "OpenAPI specification has been generated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
