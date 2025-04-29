from fastapi import FastAPI
from app.controllers.match_controller import router as match_router
from app.controllers.team_info_controller import router as team_info_router
from app.controllers.transfer_controller import router as transfer_router
from app.controllers.trophy_controller import router as trophy_router

app = FastAPI()
app.include_router(match_router)
app.include_router(team_info_router)
app.include_router(trophy_router)
app.include_router(transfer_router)

