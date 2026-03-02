import json
import random
import string
from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")
BASE_URL = "http://127.0.0.1:8000"


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def create_short_url(long_url: Annotated[str, Form()]):
    available_chars = string.ascii_letters + string.digits
    short_url = ''.join(random.choices(available_chars, k=7))

    with open("urls.json", "r") as file:
        final_urls_dict = json.loads(file.read())

        final_urls_dict[short_url] = long_url

    with open("urls.json", "w") as file:
        file.write(json.dumps(final_urls_dict))

    return {"message": f"Short URL created: {long_url}, short_url: {BASE_URL}/{short_url}"}


@app.get("/{short_url}")
async def redirect_to_long_url(short_url: str):
    with open("urls.json", "r") as file:
        final_urls_dict = json.loads(file.read())

        final_url = final_urls_dict.get(short_url)

        if final_url:
            return RedirectResponse(final_url)
        return {"message": f"Short URL not found {short_url}"}
