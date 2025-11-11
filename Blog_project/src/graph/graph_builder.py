from langgraph.graph import StateGraph,START,END
from src.llm.groq_llm import GroqLLM
from src.states.blogstate import BlogState
from src.nodes.blog_nodes import BlogNode

class GraphBuilder:
    def __init__(self,llm):
        self.llm=llm
        self.graph=StateGraph(BlogState)

    def build_topic_graph(self):
        """
        Build a graph to generate blogs based on the topic
        """
        self.blog_node_obj=BlogNode(self.llm)
        self.graph.add_node("title_creation",self.blog_node_obj.title_creation)
        self.graph.add_node("content_generation",self.blog_node_obj.content_generation)

        self.graph.add_edge(START,"title_creation")
        self.graph.add_edge("title_creation","content_generation")
        self.graph.add_edge("content_generation",END)

        return self.graph
    def build_lang_graph(self):
        """
        Build a graph for blog and graph genration with input topic with other languages 
        """

        self.blog_node_obj=BlogNode(self.llm)
        self.graph.add_node("title_creation",self.blog_node_obj.title_creation)
        self.graph.add_node("content_generation",self.blog_node_obj.content_generation)
        self.graph.add_node("japanese_translate",lambda state:self.blog_node_obj.translate({**state,"current_language":"japanese"})) ##**--> means the parameters that we give can be overwritten
        self.graph.add_node("hindi_translate",lambda state:self.blog_node_obj.translate({**state,"current_language":"hindi"}))
        self.graph.add_node("route",self.blog_node_obj.route)

        #edges and conditional edges

        self.graph.add_edge(START,"title_creation")
        self.graph.add_edge("title_creation","content_generation")
        self.graph.add_edge("content_generation","route")

        #conditional

        self.graph.add_conditional_edges(
            "route",
            self.blog_node_obj.route_decision,
            {
                "japanese":"japanese_translate",
                "hindi":"hindi_translate",
            }
        )

        self.graph.add_edge("hindi_translate",END)
        self.graph.add_edge("japanese_translate",END)
        return self.graph




    def setup_graph(self,usecase):
        if usecase=="topic":
            self.build_topic_graph()
        if usecase=="language":
            self.build_lang_graph()
        else:
            raise ValueError(f"Unknown usecase: {usecase}")
    
## Below code for the langsmith/graph studio

llm=GroqLLM().get_llm()

graph_builder=GraphBuilder(llm)
graph=graph_builder.build_lang_graph().compile()
