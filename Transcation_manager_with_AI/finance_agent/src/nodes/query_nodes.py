from src.states.transaction import TransactionState
from src.db.sheet_repository import Sheetrepository

from datetime import datetime
from typing import Dict,Any
import os
import logging

logger= logging.getLogger(__name__)

repo= Sheetrepository(
    spreadsheet=os.getenv("GOOGLE_SPREADSHEET_ID"),
    credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "service_account_credentials.json")   
)

def handle_query_node(state : TransactionState)-> Dict[str,Any]:

    query_type= state.get("query_type","unkown")
    logger.info(f"Query type : {query_type}")

    try:
        if query_type == "summary":
            results= get_summary()
        elif query_type == "ledger":
            results = get_ledger()
        elif query_type == "balance":
            results = get_balance()
        elif query_type == "filter":
            results = get_filtered(state)
        elif query_type == "category_report":
            results = get_category_report()
        else:
            results={"error":"Unknown query type"}

        reponse_manager = format_query_response(query_type,results)

        return{
            "query_results":results,
            "response_manager":reponse_manager,
            "operation_status":"success"
        }
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        return{
            "operation_status": "failed",
            "response_message": f"Error: {str(e)}"
        }
    
def get_summary()-> Dict:
    now=datetime.now()
    summary=repo.get_monthly_summary(now.year,now.month)
    return summary

def get_ledger()->Dict:
    transaction=repo.get_monthly_summary(ist=50)
    return{
        "transaction": transaction,
        "count":len(transaction)
    }

def get_balance()->Dict:
    return repo.get_total_balance()

def get_filtered(state:TransactionState)->Dict:
    category= state.get("category")

    if category:
        transactions= repo.get_transaction_by_category(category)
        return{
            "transaction":transactions,
            "filter":category,
            "count":len(transactions)
        }
    
    return{"return":"No filter specified"}

def get_category_report()->Dict:
    now=datetime.now()
    start_date= datetime(now.year,now.month,1)
    breakdown = repo.get_category_breakdown(start_date,now)
    return{"categories":breakdown}

def format_query_response(query_type: str, results:Dict)-> str:
    """Format query results into readable message"""
    if "error" in results:
        return f"{results['error']}"
    
    if query_type == "summary":
        return f"""Monthly Summary
    
    **Income:**{results.get('total_income',0):,.2f}
    **Expnse:**{results.get('total_expense',0):,.2f}
    **Net Profit:**{results.get('net_profit',0):,.2f}
    Transaction:{results.get('transaction_count',0)}
    Period{results.get('month')}/{results.get('year')}
"""
    elif query_type == "balance":
        return f"""**Overall Balance**
     **Total_Income:**{results.get('total_income',0):,.2f}
    **Totla_Expnse:**{results.get('total_expense',0):,.2f}
    **Net Balance:**{results.get('net_profit',0):,.2f}
    """

    elif query_type== "ledger":
        txns=results.get("transactions",[])[:10]
        lines=["recent Transactions"]

        for t in txns:
            lines.append(
                f"• {t['date'][:10]} | {t['type'].upper()} | "
                f"{t['category']} | ₹{t['amount']:,.2f} | {t['description']}"
            )
        
        lines.append(f"Showing {len(txns)} of {results.get('count',0)} transactions")
        return "\n".join(lines)
    
    elif query_type=="filter":
        txns=results.get("transactions",[])
        lines=[f"Filtered result : {results.get('filter')}**\n"]
        
        for t in txns[:10]:
            lines.append(
                f"• {t['date'][:10]} | ₹{t['amount']:,.2f} | {t['description']}"
            )
        
        lines.append(f"\nTotal: {results.get('count', 0)} transactions")
        return "\n".join(lines)
    
    elif query_type == "category_report":
        categories = results.get("categories", {})
        lines = ["📊 **Category Breakdown:**\n"]
        
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"**{cat}:** ₹{amount:,.2f}")
        
        return "\n".join(lines)
    
    return "Query processed successfully"

        
