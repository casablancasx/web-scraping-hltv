from fastapi import FastAPI
from app.controllers.match_controller import router as match_router
from app.controllers.team_info_controller import router as team_info_router
from app.controllers.transfer_controller import router as transfer_router
from app.controllers.trophy_controller import router as trophy_router
from app.controllers.player_controller import router as player_router
from app.controllers.championships_controller import router as championships_router

app = FastAPI()
app.include_router(match_router)
app.include_router(team_info_router)
app.include_router(trophy_router)
app.include_router(transfer_router)
app.include_router(player_router)
app.include_router(championships_router)

