from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class AINewsNode:
    def __init__(self,llm):
        """
        Initialize the AINewsNode with API key for Tavily and GROQ
        """
        self.tavily=TavilyClient()
        self.llm=llm
        self.state={}

    def fetch_news(self,state:dict)-> dict:
        """
        Fetch AI news based on the specified frequency.
        Args:
             state(dict):The state dictionary containing 'frequency'.
        Returns:
             dict:Updated state with 'news_data' key containing fetched news.
        """

        frequency = state['messages'][0].content.lower().strip()
        self.state["frequency"]=frequency
        time_range_map={'daily':'d','weekly':'w','monthly':'m','year':'y'}
        days_map={'daily':1,'weekly':7,'monthly':30,'year':366}

        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and globally",
            topics="News",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=15,
            days=days_map[frequency],
            # include_domains=["techcrunch.com", "venturebeat.com", "ai", ...] # Uncomment and add domains if needed
        )

        state['news_data']=response.get('results',[])
        self.state['news_data']=state['news_data']
        return state 
    
    def summarize_news(self,state:dict)-> dict:
        """
        Args:
            state (dict): The state dictionary containing 'news_data'.

        Returns:
            dict: updated state with 'summary' key containing the summarized news.
        """
        news_items = self.state['news_data']

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize AI news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise sentences summary from latest news
            - Source URL as link
            Use format:
            [Dated]
            [Summary](URL)"""),
            ("user", "Articles: \n{{articles}}")
        ])

        articles_str="\n\n".join([
            f"Content:{item.get('content','')}\nURL:{item.get('url','')}\nDate:{item.get('published_date','')}"
            for item in news_items
        ])

        responce=self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary']=responce.content
        self.state['summary']=state['summary']
        return self.state
    
    def save_result(self, state):
        frequency = self.state.get("frequency", "unknown")
        summary = self.state.get("summary", "")

        # Ensure directory exists
        os.makedirs("./News", exist_ok=True)

        # Simple and clean filename
        filename = f"./News/{frequency}_summary.md"

        # Write content
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        self.state["filename"] = filename
        return self.state

