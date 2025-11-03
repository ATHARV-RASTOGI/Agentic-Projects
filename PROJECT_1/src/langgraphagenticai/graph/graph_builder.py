from langgraph.graph import StateGraph,START,END
from src.langgraphagenticai.State.state import State
from src.langgraphagenticai.Nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.Tools.search_tool import get_tools,create_tool_node
from langgraph.prebuilt import tools_condition,ToolNode
from src.langgraphagenticai.Nodes.chatbot_with_tools import ChatbotTools
from src.langgraphagenticai.Nodes.ai_news_node import AINewsNode
class GraphBuilder:
    def __init__(self,model):
        self.llm=model
        self.graph_builder=StateGraph(State)

    def basic_chatbot_builder_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the 'BasicChatbotNode' class
        and integrates it into the graph. The chatbot node is set as both the
        entry and exit point of the graph.
        """

        self.basic_chatbot_node=BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)

    def Tools_chatbot(self):
        """Build an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node
        and a tool node. It defines tools, initializes the chatbot with tool
        capabilities, and sets up conditional and direct edges between nodes.
        The chatbot node is set as the entry point."""

        #Define the tool node  
        tools=get_tools()
        tool_node=create_tool_node(tools)

        llm=self.llm

        # Defining the chat bot node 
        obj_bot_wiht_node=ChatbotTools(llm)
        chatbot_node=obj_bot_wiht_node.create_chatbot(tools)
        #Add nodes
        self.graph_builder.add_node("chatbot",chatbot_node)
        self.graph_builder.add_node("tools",tool_node)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)
        
    def ai_news_graph(self):
        ai_news_node=AINewsNode(self.llm)
        self.graph_builder.add_node("fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news",ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result",ai_news_node.save_result)

        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news","summarize_news")
        self.graph_builder.add_edge("summarize_news","save_result")
        self.graph_builder.add_edge("save_result",END)



    def setup_graph(self,usecase :str):
        """
        sets up the graph for the selected use case."""

        if usecase=="Basic Chatbot":
            self.basic_chatbot_builder_graph()
        if usecase == "Advanced Chat-Bot":
            self.Tools_chatbot()
        if usecase =="AI News":
            self.ai_news_graph()
        
        
        return self.graph_builder.compile()
    
