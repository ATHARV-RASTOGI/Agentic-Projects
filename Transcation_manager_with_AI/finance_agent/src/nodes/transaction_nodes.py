from typing import Dict, Any
from datetime import datetime
import os
import logging

from src.services.date_utils import parse_date_string
from src.states.transaction import TransactionState
from src.db.sheet_repository import SheetRepository
from src.services.memory_manager import MemoryManager


logger=logging.getLogger(__name__)

repo=SheetRepository(
    spreadsheet_id=os.getenv("GOOGLE_SPREADSHEET_ID"),
    credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "service_account_credentials.json")
)

memory=MemoryManager(max_transaction=10)

def validate_transaction(state:TransactionState)->Dict:

    logger.info("Validate Node")

    error=[]

    if not state.get("amount") or state["amount"] <= 0:
        error.append("invalid amount")

    if not state.get("category"):
        error.append("Category not identified")

    if state.get("transaction_type") not in ["income", "expense"]:
        error.append("Type must be income od expence")

    if not state.get("description"):
        error.append("Description required")

    is_valid=len(error)=0

    logger.info(f"Validation:{'PASS' if is_valid else 'FAIL'}")

    return{
        "is_valid": is_valid,
        "validation_errors": error
    }

def create_pending_transaction(state: TransactionState)-> Dict[str,Any]:
    logger.info("=== CREATE PENDING TRANSACTION ===")

    if not state.get("is_valid"):
        return{
            "operation_status": "failed",
            "response_message":f"{','.join(state.get('validation_errors'))}"
        }
    
    try:
        transaction_date = parse_date_string(state.get("extracted_data")) or datetime.now()
        transaction=repo.create_transaction(
           type=state["transaction_type"],
           category=state["category"],
           amount=state["amount"],
           description=state["description"],
           date=transaction_date,
           status="pending"
        )
        memory.add_transaction(transaction)
        now=datetime.now()
        summary=repo.get_monthly_summary(now.year,now.month)

        monthly_total=summary["total_income"] if state["transaction_type"] == "income" else summary ["total_expense"]

        return{
            "transaction_id": transaction["transaction_id"],
            "operation_status": "pending_approval",
            "response_message": f"""✓ **Transaction Created (Pending Approval)**

**ID**{transaction['transaction_id']}
**Type**{state['transaction_type'].capitalize()}
**Category**{state['category']}
**Amount** ₹{state['amount']:,.2f}
**Description**{state['description']}
**Date:**{transaction_date.strftime('%Y-%m-%d')}
**Status:**

**Monthly {state['transaction_type'].capitalize()} Total:** ₹{monthly_total:,.2f}

Reply" 'approve {transaction['transaction_id']}' or 'reject{transaction['transaction_id']}'
            """
        }
    
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        return{
            "operation_status": "failed",
            "response_message": f"❌ Error: {str(e)}"
        }