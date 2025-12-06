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
