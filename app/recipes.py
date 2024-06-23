from typing import Annotated, Union, List

from fastapi import Query, APIRouter
from openai import OpenAI

from pydantic import BaseModel


class RecipeRequest(BaseModel):
    ingredients: List[str]


router = APIRouter()


@router.post("/")
def create_recipes(
    recipe_request: RecipeRequest, q: Annotated[Union[str, None], Query()] = None
):
    # uses "OPENAI_API_KEY" by default
    client = OpenAI()

    ingredients = ", ".join(recipe_request.ingredients)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a cooking assistant, with the ability to create multiple recipes from a list of ingredients.",
            },
            {
                "role": "user",
                "content": f"Using any of {ingredients} and some basic spices and kitchen implements, create 3 potential recipes.",
            },
        ],
    )

    return {"response": completion.choices[0].message.content}
