from typing import Annotated,TypedDict,Optional
from pydantic import BaseModel, Field


class Buisness(BaseModel):
        buisness:str=Field(description="what type of buisness is it ")

class InputIncomeState(TypedDict):
      income:int
      income_type:str


class InputExpenceState(TypedDict):
        expence:int
        product:str
