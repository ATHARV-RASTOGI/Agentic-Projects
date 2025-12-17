"""
Google Sheets Repository - Complete Database Layer
This is the ONLY database file you need - no SQLite!
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List,Optional,Dict
import uuid
import logging

logger = logging.getLogger(__name__)

class Sheetrepository:
    """
    Complete database operations using Google Sheets
    All methods work like SQL queries but use Sheets API
    """

    TRANSACTIONS_SHEET = "Transactions"
    RECURRING_SHEET = "Recurring"
    CATEGORIES_SHEET = "Categories"

    def __init__(self,spredsheet_id:str, credentials_path:str):
        """Initalized Google Sheets connection"""

        self.spreadsheet_id = spredsheet_id

        try:
            creds=Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.service=build('sheets','v4',credentials=creds)
            self.sheets=self.service.spreadsheets()

            logger.info(f"Connected to googel Sheets {spredsheet_id}")

        except Exception as e:
            logger.error("failed to connect to google sheets")
            raise


    def create_transcation(
           self,
           type:str,
           category:str,
           amount:float,
           description:str,
           date:Optional[datetime]=None,
           status:str = "pending"
    )->Dict:
       
       """Create new transaction"""
       transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
       transaction_date= date or datetime.now()

       row=[
           transaction_id,
           transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
           type.lower(),
           category,
           float(amount),
           description,
           status,
           ""
       ]

       try:
           self.sheets.values().append(
               spreadsheetId=self.spreadsheet_id,
               range=f'{self.TRANSACTION_SHEET}!A:H',
               valueInputOption="RAW",
               insertDateOption='INSERT_ROWS',
               body={'values':[row]}
           ).execute()

           logger.info(f"Created:{transaction_id}")

           return{
               "transaction_id":transaction_id,
               "date":transaction_id.strftime("%Y-%m-%d %H:%M:%S"),
               "type":type,
               "category":category,
               "amount":amount,
               "description":description,
               "status":status
           }
       
       except HttpError as e:
           logger.error(f"Error creating transaction:{e}")
           raise


    def get_all_trasactions (self,limit: int=100)-> List[Dict]:
        """Get all transaction (Select *)"""

        try:
            result = self.sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!A2:H{limit+1}'
            ).execute()
            
            values = result.get('values', [])
            transactions=[]

            for row in values:
                while len(row)<8:
                    row.append("")

                transactions.append({
                    "transaction_id": row[0],
                    "date": row[1],
                    "type": row[2],
                    "category": row[3],
                    "amount": float(row[4]) if row[4] else 0,
                    "description": row[5],
                    "status": row[6] if row[6] else "approved",
                    "notes": row[7]
                })

                return transactions
            
        except HttpError as e:
            logger.error(f"Error fetching transaction:{e}")
            return[]
        
    def get_transaction_by_id(self,transcation_id:str)->Optional[Dict]:
        """Find Transaction by ID"""
        transcation=self.get_all_trasactions()
        for txn in transcation:
            if txn["transaction_id"] == transcation_id: 
                return txn
        return None
    
    
    def get_pending_transactions(self) -> List[Dict]:
        """Get transactions with status='pending'"""
        all_txns = self.get_all_transactions()
        return [txn for txn in all_txns if txn.get("status") == "pending"]
    
    def get_transactions_by_category(self, category: str) -> List[Dict]:
        """Filter by category"""
        all_txns = self.get_all_transactions()
        return [txn for txn in all_txns if txn["category"] == category]
    
    def get_transaction_by_date_range(
            self,start_date: datetime,
            end_date : datetime
    ) -> List[Dict]:
        """Filter by date range"""
        all_txns = self.get_all_transactions()
        filtered = []
        for txn in all_txns:
            try:
                txn_date = datetime.strptime(txn["date"], "%Y-%m-%d %H:%M:%S")
                if start_date <= txn_date <= end_date:
                    filtered.append(txn)
            except:
                continue
        return filtered
    
    def update_transaction_status(self, transaction_id: str,new_status : str)->bool:
        """Update ststus column"""
        try:
            all_data=self.sheets.value().get(
                spreadsheetID=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!A:A'
            ).execute().get('values',[])

            row_number=None
            for idx,row in enumerate(all_data):
                if row and row[0] == transaction_id:
                    row_number= idx+1
                    break
            
            if not row_number:
                return False
            
            self.sheets.values().update(
                spreadsheetID=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!G{row_number}',
                valueInputOption='RAW',
                body={'values':[[new_status]]}
            ).execute()

            logger.info(f" Update {transaction_id}-> {new_status}")
            return True
        except HttpError as e:
            logger.error(f"Error Updateing {e}")
            return False
        
    def edit_transction(
            self,
            transaction_id:str,
            category :Optional[str]= None,
            amount: Optional[float]=None,
            description : Optional[str]= None
    )-> bool:
        """Edit transaction fields"""
        try:
            all_data=self.sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!A:H'
            ).execute().get('values',[])

            row_number = None
            for idx, row in enumerate(all_data):
                if row and row[0] == transaction_id:
                    row_number = idx + 1
                    break
            
            if not row_number:
                return False
            
            if category:
                self.sheets.values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f'{self.TRANSACTIONS_SHEET}!D{row_number}',
                    valueInputOption='RAW',
                    body={'values': [[category]]}
                ).execute()
            
            if amount is not None:
                self.sheets.values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f'{self.TRANSACTIONS_SHEET}!E{row_number}',
                    valueInputOption='RAW',
                    body={'values': [[amount]]}
                ).execute()
            
            if description:
                self.sheets.values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f'{self.TRANSACTIONS_SHEET}!F{row_number}',
                    valueInputOption='RAW',
                    body={'values': [[description]]}
                ).execute()
            
            logger.info(f"✓ Edited {transaction_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error editing: {e}")
            return False
        
    def delete_transaction(self,transaction_id:str)->bool:
        """Delete transactoin (for undo)"""
        try:
            all_data=self.sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!A:A'
            ).execute().get('values',[])

            row_number=None
            for idx,row in enumerate(all_data):
                if row and row[0] == transaction_id:
                    row_number= idx+1
                    break
            
            if not row_number:
                return False
            
            request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": self._get_sheet_id(self.TRANSACTIONS_SHEET),
                        "dimension": "ROWS",
                        "startIndex": row_number - 1,
                        "endIndex": row_number
                    }
                }
            }

            self.sheets.batchUpdate(
                spradsheetId=self.spreadsheet_id,
                body={"requests":[request]}
            ).execute()

            logger.info(f"Deleted {transaction_id}")
            return True
        
        except HttpError as e:
            logger.error(f"Error deleteing {e}")
            return False
    
    def get_monthly_summary(self,year:int , month:int)->Dict:
        """Geey monthly income /expense summary"""
        all_txns=self.get_all_trasactions()

        total_income=0
        total_expense=0
        count=0

        for txn in all_txns:
            try:
                txn_data=datetime.strptime(txn["date"],"%Y-%m-%d %H:%M:%S")

                if txn_data.year == year and txn_data.month == month:
                    count+= 1
                    if txn["type"] == "income":
                        total_income += txn["amount"]
                    elif txn["type"] == "expense":
                        total_expense += txn["amount"]
            except:
                continue
        
        return {
            "year": year,
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_profit": total_income - total_expense,
            "transaction_count": count
        }
    
    def get_total_balance(self) -> Dict:
        """Get overall balance"""
        all_txns = self.get_all_transactions()
        
        total_income = sum(txn["amount"] for txn in all_txns if txn["type"] == "income")
        total_expense = sum(txn["amount"] for txn in all_txns if txn["type"] == "expense")
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": total_income - total_expense
        }
    
    def get_category_breakdown(
            self,
            start_date:datetime,
            end_date:datetime,
            transactoin_type : Optional[str]=None
    )-> Dict[str,float]:
        """Category-wise summary"""
        txns = self.get_transactions_by_date_range(start_date, end_date)


    def create_recurring_transaction(
        self,
        type: str,
        category: str,
        amount: float,
        description: str,
        frequency: str,
        next_date: datetime
    ) -> Dict:
        """Create recurring transaction template"""
        recurring_id = f"REC-{uuid.uuid4().hex[:6].upper()}"
        
        row = [
            recurring_id,
            type,
            category,
            amount,
            description,
            frequency,
            next_date.strftime("%Y-%m-%d")
        ]
        
        try:
            self.sheets.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.RECURRING_SHEET}!A:G',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
            
            logger.info(f"✓ Created recurring: {recurring_id}")
            
            return {
                "recurring_id": recurring_id,
                "frequency": frequency,
                "next_date": next_date.strftime("%Y-%m-%d")
            }
            
        except HttpError as e:
            logger.error(f"Error creating recurring: {e}")
            raise

    def get_sheet_id(self, sheet_name:str)-> int:
        """Get internal sheet ID"""
        try:
            metadata= self.sheets.get(spreadsheetID=self.spreadsheet_id).execute()
            for sheets in metadata['sheets']:
                if sheets['properties']['title']== sheet_name:
                    return sheet_name['properties']['sheetId']
            return 0
        except:
            return 0
        
    def initialize_sheets(self):
        """Create headers (run once)"""

        try:
            headers=[[
                "Transaction_ID", "Date", "Type", "Category",
                "Amount", "Description", "Status", "Notes"
            ]]
            self.sheets.values().update(
                 spreadsheetId=self.spreadsheet_id,
                range=f'{self.TRANSACTIONS_SHEET}!A1:H1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()

            logger.info("✓ Sheet headers initialized")
            
        except HttpError as e:
            logger.error(f"Error initializing: {e}")
    

    def process_recurring_transactions(self) -> List[str]:
        """Process due recurring transactions"""
        try:
            result = self.sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.RECURRING_SHEET}!A2:G'
            ).execute()
            
            recurring_txns = result.get('values', [])
            created_ids = []
            today = datetime.now().date()
            
            for row in recurring_txns:
                if len(row) < 7:
                    continue
                
                next_date = datetime.strptime(row[6], "%Y-%m-%d").date()
                
                if next_date <= today:
                    txn = self.create_transaction(
                        type=row[1],
                        category=row[2],
                        amount=float(row[3]),
                        description=row[4],
                        status="approved"
                    )
                    created_ids.append(txn["transaction_id"])
            
            return created_ids
            
        except HttpError as e:
            logger.error(f"Error processing recurring: {e}")
            return []