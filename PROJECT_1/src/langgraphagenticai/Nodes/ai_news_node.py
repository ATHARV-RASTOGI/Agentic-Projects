from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class AINewsNode:
    def __init__(self, llm):
        """
        Initialize the AINewsNode with API key for Tavily and GROQ
        """
        self.tavily = TavilyClient()
        self.llm = llm

    def fetch_news(self, state: dict) -> dict:
        """
        Fetch AI news based on the specified frequency.
        Args:
             state(dict): The state dictionary containing 'frequency'.
        Returns:
             dict: Updated state with 'news_data' key containing fetched news.
        """
        frequency = state['messages'][0].content.lower().strip()
        state["frequency"] = frequency
        
        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

        print(f"🔍 Fetching {frequency} AI news...")
        
        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and globally",
            topics="News",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=15,
            days=days_map[frequency],
        )

        news_data = response.get('results', [])
        print(f"📰 Found {len(news_data)} articles")
        
        # Debug: Print first article
        if news_data:
            print(f"Sample article: {news_data[0].get('title', 'No title')[:100]}...")
            print(f"Published: {news_data[0].get('published_date', 'No date')}")
        
        state['news_data'] = news_data
        return state 
    
    def summarize_news(self, state: dict) -> dict:
        """
        Args:
            state (dict): The state dictionary containing 'news_data'.

        Returns:
            dict: updated state with 'summary' key containing the summarized news.
        """
        news_items = state.get('news_data', [])
        
        # Check if we have news items
        if not news_items:
            state['summary'] = "No news articles found for the specified timeframe."
            return state

        # Format articles with better structure
        articles_list = []
        for idx, item in enumerate(news_items, 1):
            article = f"""
Article {idx}:
Title: {item.get('title', 'No title')}
Content: {item.get('content', 'No content available')}
Published Date: {item.get('published_date', 'Unknown date')}
URL: {item.get('url', 'No URL')}
---"""
            articles_list.append(article)
        
        articles_str = "\n".join(articles_list)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a news summarizer. Create a markdown summary of the provided AI news articles.

CRITICAL INSTRUCTIONS:
- Use ONLY the articles provided below
- DO NOT make up or hallucinate any information
- For each article, include:
  * Date in YYYY-MM-DD format (convert to IST timezone if needed)
  * A concise 1-2 sentence summary of the actual article content
  * The actual source URL provided

Format each entry as:
[YYYY-MM-DD]
[Your concise summary of the article](actual_url)

If an article doesn't have a date, use "Unknown Date".
If an article doesn't have content, skip it."""),
            ("user", "Here are the articles to summarize:\n\n{articles}\n\nNow create the markdown summary following the format specified.")
        ])

        response = self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary'] = response.content
        return state
    
    def save_result(self, state):
        frequency = state.get("frequency", "unknown")
        summary = state.get("summary", "")

        # Ensure directory exists
        os.makedirs("./News", exist_ok=True)

        # Simple and clean filename
        filename = f"./News/{frequency}_summary.md"

        # Write content
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        state["filename"] = filename
        return state