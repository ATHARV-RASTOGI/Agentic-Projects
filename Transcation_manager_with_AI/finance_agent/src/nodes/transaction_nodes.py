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
    
def approve_transaction_node(state:TransactionState)->Dict[str,Any]:
    logger.info("--Approve transaction--")

    user_input=state.get("user_input","")
    parts=user_input.split()

    if len(parts)<2:
        return {"responce_message":"Usage approve TXN"}
    
    transaction_id=parts[1]

    try:
        success= repo.update_transaction(transaction_id,"approved")

        if success:
            for txn in memory.recent_transactions:
                if txn ["transaction_id"]== transaction_id:
                    txn["status"]="approved"

            return {
            "operation_status":"success",
            "response_manager":f"**Transaction Approved {transaction_id} \nStatus: Approved"
            }
        else:
            return {"response_message": f"❌ Transaction {transaction_id} not found"}
            
    except Exception as e:
        return{"responce_manager": f"Error{str(e)}"}

def reject_transasction_node(state:TransactionState)-> Dict[str,Any]:
    """---Reject and delete pending transaction---"""
    logger.info("==Reject Transaction==")

    user_input=state.get("user_input")
    parts=user_input.split()

    if len(parts)<2:
        return{"responce_message":"Reject the TXN"}
    
    transaction_id = parts[1]
    
    try:
        success = repo.delete_transaction(transaction_id)
        
        if success:
            return {
                "operation_status": "success",
                "response_message": f"🗑️ **Transaction Rejected**\n\nID: {transaction_id}\nStatus: Deleted"
            }
        else:
            return {"response_message": f"❌ Transaction {transaction_id} not found"}
            
    except Exception as e:
        return {"response_message": f"❌ Error: {str(e)}"}
    
def show_pending_transaction(state:TransactionState)->Dict[str,Any]:
    """Show all pending transaction"""
    logger.info("Show_transaction")

    try:
        pending=repo.get_pending_transactions()

        if not pending:
            return{"response_message":"No prnding tranasction"}
        
        lines=["Pending Transactions"]

        for txn in pending :
            lines.append(
                f"{txn['transaction_id']} | {txn["type"].upper()} | "
                f"{txn["category"]} | ₹{txn["amount"]:,.2f} | {txn['description']}"
            )
        lines.append("Replly :'approvr TXN-ID or 'reject TXN-ID'")

        return{
            "response_message":"\n".join(lines),
            "query_results":{"pending_transactions":pending}
        }
    
    except Exception as e:
        return{"response_message": f"Error:{str(e)}"}
    
def undo_last_transaction_node(state:TransactionState)-> Dict[str,Any]:

    try:
        last_txn= memory.get_last_transaction()

        if not last_txn:
            return{"responce_message":"No recent transaction to undo"}
        
        transaction_id=last_txn["transaction_id"]
        success=repo.delete_transaction(transaction_id)

        if success :
            if last_txn in memory.recent_transactions:
                memory.recent_transactions.remove(last_txn)
            
            return{
                "operation_status": "success",
                "response_message": f"""🔄 **Transaction Undone**

                **Deleted:** {transaction_id}
                - Type: {last_txn['type']}
                - Category: {last_txn['category']}
                - Amount: ₹{last_txn['amount']:,.2f}
                - Description: {last_txn['description']}
                """
            }
        else:
            return{"response_message": f"❌ Could not delete {transaction_id}"}
        
    except Exception as e:
        return {"response_message": f"❌ Error: {str(e)}"}
    
def edit_transaction_node(state:TransactionState)->Dict[str,Any]:
    logger.info("==EDIT TRANSACTION==")

    user_input=state.get("user_input")
    parts= user_input.split()

    if len(parts)<4 :
        return{
            "response_manager":"""Invalid Format
            
            Usage:
            -  edit TXN-12345 amount 5000
            - edit TXN-12345 category Rent
            - edit TXN-12345 description "New text"
              
            """
        }
    
    transaction_id=parts[1]
    field= parts[2].lower()
    value="".join(parts[3:].strip('"'))

    try:
        if field =="amount":
            success= repo.edit_tranasction(transaction_id, amount=float(value))
        elif field == "category":
            success=repo.edit_tranasction(transaction_id, category=value)
        elif field=="description":
            success=repo.edit_transaction(transaction_id,description=value)
        else:
            return{"response_message":f"Unknown Field{field}"}
        
        if success:
            for txn in memory.recent_transactions:
                if txn["transaction_id"]== transaction_id:
                    if field == "amount":
                        txn["amount"]= float(value)
                    elif field == "category":
                        txn["category"]=value
                    elif field == "description":
                        txn["description"]= value

            return{
                "operation_statue":"success",
                "response_message": f"✏️ **Transaction Updated**\n\nID: {transaction_id}\nUpdated: {field} = {value} "
            }
        else:
            return{"response_message": f"❌ Transaction {transaction_id} not found"}
    except Exception as e:
        return{"response_message": f"❌ Error: {str(e)}"}


def create_recurring_transaction_node(state:TransactionState)-> Dict[str,Any]:

    logger.info("=CREATE RECURRING=")

    user_input=state.get("user_input")
    parts=user_input.lower().split()

    if len(parts)<6 :
        return{
            "response_message":"""Invalid Format

            Usage :Create recurring [type] [category] [amount] [frequency]
            Example : create recurring expence Rent 12000 monthly
            """
        }
    
    try:
        txn_type=parts[2]
        category=parts[3].capitalize
        amount= float(parts[4])
        frequency=parts[5]

        next_date =datetime.now()
        description= f" Recurring {category} ({frequency})"

        result= repo.create_recurring_transaction(
            type=txn_type,
            category=category,
            amount=amount,
            frequency=frequency,
            description=description,
            next_date=next_date
        )

        return{
             "operation_status": "success",
            "response_message": f"""🔄 **Recurring Transaction Created**

            **ID:** {result['recurring_id']}
            **Type:** {txn_type.capitalize()}
            **Category:** {category}
            **Amount:** ₹{amount:,.2f}
            **Frequency:** {frequency.capitalize()}
            **Next Due:** {result['next_date']}

            Will auto-process on due date.
            """
        }
    except Exception as e:
        return{"response_message":f"Error {str(e)}"}

def show_recent_transaction_node(state:TransactionState)-> Dict[str,Any]:

    recent= memory.get_recent_trasactions(count=10)

    if not recent:
        return{"response_manager":"No recent transaction in memory"}

    lines=["Return Transations (Memory)"]

    for txn in reversed(recent):
        lines.append(
            f"**{txn['transaction_id']}** | {txn['date'][:10]} | "
            f"{txn['type'].upper()} | {txn['category']} | ₹{txn['amount']:,.2f}"
        )
    
    return {"response_message": "\n".join(lines)}

