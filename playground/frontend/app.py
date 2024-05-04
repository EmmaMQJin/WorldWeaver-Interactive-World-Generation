from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json  # Import JSON for serialization

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variable to hold character data
main_character = {
    "name": "Unknown",
    "description": "No character has been created yet."
}

def generate_main_character(background_story):
    return {
        "name": "Hero",
        "description": "A brave warrior with a mysterious past based on: " + background_story
    }

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit-background-story")
async def submit_background_story(background_story: str = Form(...)):
    global main_character
    main_character = generate_main_character(background_story)
    return RedirectResponse(url="/display-character", status_code=303)

@app.get("/display-character")
async def display_character(request: Request):
    return templates.TemplateResponse("display_character.html", {"request": request, "main_character": main_character})

@app.post("/update-character")
async def update_character(request: Request, name: str = Form(...), description: str = Form(...)):
    global main_character
    main_character["name"] = name
    main_character["description"] = description
    return RedirectResponse(url="/display-character", status_code=303)

@app.get("/initial-state")
async def get_initial_state(request: Request):
    # Deserialize the main_character dictionary from the cookie
    main_character_json = request.cookies.get("main_character", "{}")
    main_character = json.loads(main_character_json)
    return templates.TemplateResponse("initial_state.html", {"request": request, "main_character": main_character})

@app.post("/submit-initial-state")
async def submit_initial_state(request: Request, response: Response, initial_state: str = Form(...)):
    response.set_cookie(key="initial_state", value=initial_state, max_age=1800)  # 30 minutes expiration
    return RedirectResponse(url="/winning-state", status_code=303)

@app.get("/winning-state")
async def get_winning_state(request: Request):
    initial_state = request.cookies.get("initial_state", "No initial state provided")
    return templates.TemplateResponse("winning_state.html", {"request": request, "initial_state": initial_state})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
