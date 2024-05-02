from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit-description")
async def submit_description(request: Request):
    data = await request.json()
    description = data.get("description", "")
    print("Received description:", description)
    return templates.TemplateResponse("character_description.html", {"request": request, "description": description})

@app.get("/character-description")
async def character_description(request: Request):
    return templates.TemplateResponse("character_description.html", {"request": request, "description": ""})

@app.get("/list-page")
async def get_list_page(request: Request):
    # This assumes list.html is located in the 'templates' directory
    return templates.TemplateResponse("list.html", {"request": request})