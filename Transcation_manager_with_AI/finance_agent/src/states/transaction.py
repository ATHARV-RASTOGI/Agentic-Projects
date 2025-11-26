from typing import Annotated,Optional,Literal
from pydantic import BaseModel, Field
from datetime import datetime
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

##Input validation of data ##

class Buisness(BaseModel):
        "Buisness profile"
        buisness_name:str=Field(description="Name of buisness")
        buisness_type:str=Field(description="Type of buisness")

class Transaction(BaseModel):
        "Individual Transaction Records"

        transaction_id:Optional[str]=None
        data:datetime=Field(default=datetime.now)
        type:Literal["income","expense"]=Field(description="Type of transaction")
        category:str=Field(description="Business category (e.g., Sales Revenue, Raw Materials)")
        amount:float=Field(description="Transaction description")
        descreption:str=Field(description="Transaction description")
        payment_type:Optional[str]=Field(default="Cash", description="Payment_mode : Online, Card")

        class Config:
                json_encoders = {
            datetime: lambda v: v.isoformat()
        }

##Langraph_State

class TransactionState(TypedDict):
        """Main state for the langgraph workflow"""

        message:Annotated[list,add_messages]
        user_input:str

        transaction_type:Optional[Literal["income","expence","query","unknown"]]
        category:Optional[str]
        amount:Optional[str]
        description:Optional[str]
        extracted_data:Optional[str]

        transaction_id:Optional[str]
        operation_status:Optional[str]

        query_type:Optional[str]
        query_result:Optional[dict]

        responce_message:str
        next_action:Optional[str]

class SummaryState(TypedDict):
        """Format for asking of summary"""
        period:str
        start_data:Optional[datetime]
        end_date:Optional[datetime]
        category_filter:Optional[str]

        total_income:float
        totla_expence:float
        net_profit:float
        transaction:list[dict]
        category_breakdown:dict[str,float]

INCOME_CATEGORIES = [
    "Sales Revenue",
    "Client Payments",
    "Service Income",
    "Consulting Fees",
    "Interest Income",
    "Other Business Income"
]

EXPENSE_CATEGORIES = [
    "Raw Materials",
    "Utilities",
    "Transportation",
    "Employee Salaries",
    "Maintenance",
    "Rent",
    "Marketing",
    "Office Supplies",
    "Professional Fees",
    "Bank Charges",
    "Miscellaneous"
]

def create_initial_state()->TransactionState:
        return TransactionState(
                messages=[],
                user_input="",
                transaction_type=None,
                category=None,
                amount=None,
                description=None,
                extracted_date=None,
                is_valid=False,
                validation_errors=[],
                transaction_id=None,
                operation_status=None,
                query_type=None,
                query_results=None,
                response_message="",
                next_action=None
        )

def is_query(text:str)->bool:
        """Check if input is a query rathe than transaction entry """
        query_keywords=[
               "show", "display", "what", "how much", "total", "summary",
        "report", "ledger", "balance", "profit", "list", "filter"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in query_keywords)   
        