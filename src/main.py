import random
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import AfterValidator 


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


app = FastAPI()


def check_valid_id(id: str) -> str:
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get('/')
def read_root():
    return {"Hello": "World"}


@app.get('/items/')
async def read_items(
    id: Annotated[
        str | None, 
        AfterValidator(check_valid_id),
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_lenght=3,
        ),
    ] = None):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {'id': id, 'name': item}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
