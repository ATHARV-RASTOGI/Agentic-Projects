from pydantic import BaseModel ,Field
from typing_extensions import TypedDict,Annotated
from langgraph.graph.message import add_messages



class State(TypedDict):
    """
    Represent the structure of the state used in graph
    """

    message:Annotated[list,add_messages]