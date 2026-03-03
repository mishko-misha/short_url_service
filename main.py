import random
import string
from typing import Annotated

import pymongo
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")
BASE_URL = "http://127.0.0.1:8000"

client = pymongo.AsyncMongoClient("mongodb://admin:password@localhost:27017")
shorter_urls_db = client["shorter_urls_db"]
urls_collection = shorter_urls_db["urls"]


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def create_short_url(long_url: Annotated[str, Form()]):
    available_chars = string.ascii_letters + string.digits

    short_url = ''.join(random.choices(available_chars, k=7))
    while await urls_collection.find_one({"short_url": short_url}) is not None:
        short_url = ''.join(random.choices(available_chars, k=7))

    final_document = {"short_url": short_url, "long_url": long_url, "clicks": 0}

    await urls_collection.insert_one(final_document)

    return {"message": f"Short URL created: {long_url}, short_url: {BASE_URL}/{short_url}"}


@app.get("/{short_url}")
async def redirect_to_long_url(short_url: str):
    final_urls_dict = await urls_collection.find_one({"short_url": short_url})

    if final_urls_dict:
        query_filter = {"short_url": short_url}
        await urls_collection.update_one(query_filter, {"$inc": {"clicks": 1}})
        final_url = final_urls_dict.get("long_url")

        return RedirectResponse(final_url)
    return {"message": f"Short URL not found {short_url}"}
