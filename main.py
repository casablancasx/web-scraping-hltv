# package: <root>
# file: main.py
from fastapi import FastAPI
from app.controllers import ( # Group imports
    match_controller,
    team_info_controller,
    transfer_controller,
    trophy_controller,
    player_controller,
    championships_controller,
    news_controller,
    coach_controller
)


app = FastAPI(
    title="HLTV Scraper API",
    description="API to scrape Counter-Strike data from HLTV and Draft5 for FURIA.",
    version="0.1.0" 
)

app.include_router(match_controller.router)
app.include_router(team_info_controller.router)
app.include_router(trophy_controller.router)
app.include_router(transfer_controller.router)
app.include_router(player_controller.router)
app.include_router(championships_controller.router)
app.include_router(news_controller.router)
app.include_router(coach_controller.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
