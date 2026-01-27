import random
from typing import Annotated

from fastapi import FastAPI, Query, Path, Body
from pydantic import AfterValidator, BaseModel, Field, HttpUrl


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


app = FastAPI()

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
    images: list[Image]


class User(BaseModel):
    username: str
    full_name: str | None = None


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


@app.put("/v1/items/{item_id}")
async def update_item_v1(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    query: str | None = None,
    item: Item | None = None, 
):
    results = { "item_id": item_id }

    if query:
        results.update({"query": query})
    
    if item:
        results.update({"item": item})

    return results


@app.put("/v2/items/{item_id}")
async def update_item_v2(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}


    return results

@app.put("/v3/items/{item_id}")
async def update_item_v3(
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}

    if q:
        results.update({"q": q})
    
    return results


@app.put("/v4/items/{item_id}")
async def update_item_v4(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}

    return results


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]) -> list[Image]:
    return images