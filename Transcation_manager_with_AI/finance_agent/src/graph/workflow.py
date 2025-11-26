from src.states.transaction import TransactionState,Transaction,SummaryState,create_initial_state,is_query
from langgraph.graph import START,END,StateGraph
import logging
from typing import Literal
from datetime import datetime
from src.nodes.classify_input import classify_input_node
from src.nodes.transaction_nodes import (
    edit_transaction,
    create_pending_transaction,
    approve_transcation,
    reject_transaction,
    show_pending_transaction,
    undo_transaction,
    recurring_transaction,
    recent_transaction
)
from src.nodes.query_nodes import handle_query_node

logger= logging.getLogger(__name__)

def start_node(state:TransactionState)-> dict:
    

    user_input=state.get("user_input")
    user_lower=user_input.lower()

    if not user_input:
        return{
            "is_valid":False,
            "response_message":"No transaction recieved",
            "next_action":"END"
        }
    
    if user_lower.startswith("undo"):
        return{"next_action":"undo"}
    
    if user_lower.startswith("edit"):
        return{"next_action":"edit"}
    
    if user_lower.startswith("approve"):
        return{"next_actoin":"approve"}
    
    if "show pending" in user_lower or "pending transactions" in user_lower:
        return {"next_action": "show_pending"}
    
    if "create recurring" in user_lower:
        return {"next_action": "create_recurring"}
    
    if "recent" in user_lower and "transaction" in user_lower:
        return {"next_action": "show_recent"}
    
    # Default: classify
    return {"is_valid": True, "next_action": "classify"}

    
def start_router(state:TransactionState) -> Literal[
    "classify","undo","edit","approve","reject",
    "show_pending","create_recurring", "show_recent", "end"
]:
    """Route Starter"""
    next_action=state.get("next_action","classify")
    logger.info(f"START->{next_action.upper}")
    return next_action

def classify_router(state:TransactionState)-> Literal["validate","handel_query","end"]:

    txn_type=state.get("transaction_type")

    if txn_type in ["income","expense"]:
        logger.info("CLASSIFY -> VALIDATE")
        return "validate"
    elif txn_type in ["query"]:
        logger.info("CLASSIFY -> QUERY")
        return "handel_query"
    else:
        logger.info("CLASSIFY -> END")
        return "end"
    
def validation_router(state:TransactionState) -> Literal["create_pending","end"]:

    is_valid = state.get("is_valid", False)
    
    if is_valid:
        logger.info("VALIDATE → CREATE_PENDING")
        return "create_pending"
    else:
        logger.info("VALIDATE → END (failed)")
        return "end"
  
def build_workflow()->StateGraph:


    """
    Build complete workflow
    
    Flow:
    START → [classify, undo, edit, approve, reject, show_pending, recurring, recent]
      ├─ classify → validate → create_pending → END
      └─ All others → END
    """

    workflow=StateGraph(TransactionState)
    workflow.add_node("start",start_node)
    workflow.add_node("calssify",classify_input_node)
    workflow.add_node("validate",edit_transaction)
    workflow.add_node("create_pending",create_pending_transaction)
    workflow.add_node("handle_query",handle_query_node)
    workflow.add_node("approve",approve_transcation)
    workflow.add_node("reject",reject_transaction)
    workflow.add_node("show_pending",show_pending_transaction)
    workflow.add_node("undo",undo_transaction)
    workflow.add_node("edit",edit_transaction)
    workflow.add_node("create_recurring",recurring_transaction)
    workflow.add_node("show_recent",recent_transaction)

    workflow.set_entry_point("start")

    workflow.add_conditional_edges(
        #creates automatic connection b/w start node and start-router 
        "start",start_router,
        {
            "classify": "classify",
            "undo": "undo",
            "edit": "edit",
            "approve": "approve",
            "reject": "reject",
            "show_pending": "show_pending",
            "create_recurring": "create_recurring",
            "show_recent": "show_recent",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "classify",
        classify_router,
        {
            "validate": "validate",
            "handle_query": "handle_query",
            "end": END
        }
    )
    
   
    workflow.add_conditional_edges(
        "validate",
        validation_router,
        {
            "create_pending": "create_pending",
            "end": END
        }
    )

    workflow.add_edge("create_pending", END)
    workflow.add_edge("handle_query", END)
    workflow.add_edge("undo", END)
    workflow.add_edge("edit", END)
    workflow.add_edge("approve", END)
    workflow.add_edge("reject", END)
    workflow.add_edge("show_pending", END)
    workflow.add_edge("create_recurring", END)
    workflow.add_edge("show_recent", END)

    app = workflow.compile()
    
    logger.info("✓ Workflow compiled successfully")
    return app

def process_input(user_input :str)-> dict:
    """
    Main entry point - process user input
    
    Args:
        user_input: Natural language command
    
    Returns:
        Final state with response_message
    """
     
    initial_state = create_initial_state()
    initial_state["user_input"]=user_input

    app=build_workflow()
    try:
        final_state = app.invoke(initial_state)
        
        logger.info(f"\n{'='*60}")
        logger.info("✓ WORKFLOW COMPLETED")
        logger.info(f"{'='*60}\n")
        
        return final_state
        
    except Exception as e:
        logger.error(f"❌ Workflow error: {e}", exc_info=True)
        return {
            "response_message": f"❌ Error: {str(e)}",
            "operation_status": "failed"
        }