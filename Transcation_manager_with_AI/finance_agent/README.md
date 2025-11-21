# 💼 Business Accounting Chat Assistant

A **Tally-style accounting system** powered by LangGraph, LLMs, and Streamlit. Chat naturally to record transactions, generate reports, and manage your business finances.

---

## 🎯 Features

### ✅ Core Capabilities
- **Natural Language Transaction Entry**: Just type "Received payment 30000" or "Electricity bill 1200"
- **Automatic Classification**: AI automatically categorizes income/expenses
- **Smart Date Parsing**: Supports "yesterday", "last Monday", specific dates
- **Business Accounting Categories**: Proper income/expense classification
- **Real-time Reporting**: Monthly summaries, ledgers, balance sheets
- **Persistent Storage**: SQLite database for all transactions
- **Beautiful Chat UI**: Streamlit-based conversational interface

### 📊 Accounting Features
- Income tracking with categories (Sales, Client Payments, etc.)
- Expense tracking with categories (Raw Materials, Salaries, etc.)
- Monthly/Quarterly/Yearly summaries
- Category-wise breakdowns
- Net profit/loss calculations
- Full ledger views
- Transaction filtering

---

## 🚀 Quick Start

### 1. **Clone & Setup**

```bash
# Navigate to your project
cd finance_agent

# Activate virtual environment (if using venv)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using uv
uv venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# or with uv
uv pip install -r requirements.txt
```

### 2. **Environment Configuration**

Create a `.env` file in the root directory:

```env
# LLM Provider API Keys
GROQ_API_KEY=your_groq_api_key_here

# Optional: If using Ollama locally
# OLLAMA_BASE_URL=http://localhost:11434

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./finance_agent.db

# Logging
LOG_LEVEL=INFO
```

**Get GROQ API Key:**
1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Add to `.env` file

### 3. **Initialize Database**

The database will auto-initialize on first run, but you can also manually initialize:

```python
from src.db.models import init_database

# This creates finance_agent.db in your root directory
engine, SessionLocal = init_database()
print("Database initialized!")
```

### 4. **Run the Application**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
finance_agent/
│
├── .venv/                          # Virtual environment
├── .env                            # Environment variables (create this)
│
├── src/
│   ├── states/
│   │   └── transaction_state.py    # State definitions
│   │
│   ├── llm/
│   │   ├── model_loader.py         # LLM initialization
│   │   └── prompts.py              # Structured prompts
│   │
│   ├── nodes/
│   │   ├── classify_input.py       # Classification node
│   │   └── validate_insert_nodes.py # DB operation nodes
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py               # SQLAlchemy models
│   │   └── repository.py           # Database operations
│   │
│   ├── services/
│   │   └── date_utils.py           # Date parsing
│   │
│   └── graph/
│       └── workflow.py             # LangGraph workflow
│
├── app.py                          # Streamlit UI
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 💡 Usage Examples

### Adding Transactions

```
User: "Received payment from client 30000"
Assistant: ✓ Entry recorded!
Type: Income | Category: Client Payments | Amount: ₹30,000
Monthly Total (Income): ₹45,000

User: "Purchased raw materials 4500"
Assistant: ✓ Entry recorded!
Type: Expense | Category: Raw Materials | Amount: ₹4,500
Monthly Total (Expense): ₹12,300

User: "Salary to employees 18000 yesterday"
Assistant: ✓ Entry recorded!
[Records with yesterday's date]
```

### Querying Reports

```
User: "Show me this month's summary"
Assistant: 📊 Monthly Summary
Total Income: ₹75,000
Total Expense: ₹45,000
Net Profit: ₹30,000

User: "How much did we spend on raw materials?"
Assistant: [Shows filtered transactions for Raw Materials category]

User: "What is the current balance?"
Assistant: 💰 Overall Balance
Total Income: ₹2,50,000
Total Expense: ₹1,80,000
Net Balance: ₹70,000
```

---

## 🛠️ Advanced Configuration

### Using Ollama (Local LLM)

If you prefer running models locally:

```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2

# Update src/llm/model_loader.py
# Change provider to "ollama" in get_llm() calls
```

### Custom Categories

Edit `src/states/transaction_state.py`:

```python
INCOME_CATEGORIES = [
    "Sales Revenue",
    "Your Custom Category",
    # ... add more
]

EXPENSE_CATEGORIES = [
    "Raw Materials",
    "Your Custom Expense",
    # ... add more
]
```

### Database Configuration

For PostgreSQL/MySQL instead of SQLite:

```python
# In .env
DATABASE_URL=postgresql://user:pass@localhost/finance_db

# Or MySQL
DATABASE_URL=mysql+pymysql://user:pass@localhost/finance_db
```

---

## 🧪 Testing the Workflow

Test individual components:

```python
from src.graph.workflow import process_input

# Test transaction
result = process_input("Received payment 5000")
print(result["response_message"])

# Test query
result = process_input("Show this month's summary")
print(result["response_message"])
```

---

## 📊 Categories Reference

### Income Categories
- Sales Revenue
- Client Payments
- Service Income
- Consulting Fees
- Interest Income
- Other Business Income

### Expense Categories
- Raw Materials
- Utilities (electricity, water, internet)
- Transportation
- Employee Salaries
- Maintenance
- Rent
- Marketing
- Office Supplies
- Professional Fees
- Bank Charges
- Miscellaneous

---

## 🔧 Troubleshooting

### Database Issues
```bash
# Delete and reinitialize database
rm finance_agent.db
python -c "from src.db.models import init_database; init_database()"
```

### LLM Connection Issues
```bash
# Verify GROQ API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"

# Test Ollama connection
curl http://localhost:11434/api/tags
```

### Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with debug logging
streamlit run app.py --logger.level=debug
```

---

## 🚀 Next Steps & Enhancements

### Planned Features
- [ ] Export to Excel/PDF
- [ ] Multi-user support
- [ ] Invoice generation
- [ ] GST calculations
- [ ] Bank reconciliation
- [ ] Automated backups
- [ ] Mobile app
- [ ] Voice input
- [ ] Multi-language support

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📝 License

This project is open-source and available under the MIT License.

---

## 🤝 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check documentation
- Review example code

---

**Built with ❤️ using LangGraph, LangChain, Streamlit**