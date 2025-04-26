from fastapi import FastAPI
from app.controllers.match_controller import router as match_router
from app.controllers.team_info_controller import router as team_info_router
from app.controllers.transfer_controller import router as transfer_router

app = FastAPI()
app.include_router(match_router)
app.include_router(team_info_router)

app.include_router(transfer_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
