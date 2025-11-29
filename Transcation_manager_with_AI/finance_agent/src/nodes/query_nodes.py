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
            results = get_categorty_report()
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
    

