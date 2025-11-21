from src.langgraphagenticai.State import state

class ChatbotTools:
    def __init__(self,model):
        self.llm=model

    def process(self,state:state)->dict:
        """ Process the input state and generate a chatbot response."""
    
        user_input=state["messages"][-1] if state["messages"] else ""
        llm_response= self.llm.invoke([{"role":"user","content":user_input}])

        tools_response= f"tool integration for:{user_input}"

        return {"messages":[llm_response,tools_response]}
    
    def create_chatbot(self,tools):
        """
        Return a chatbot node function 
        """
        llm_with_tools=self.llm.bind_tools(tools)

        def chatbot_node(state:state):
            """
            Chatbot logic for proessing the input state and returning a response.
            """

            return {"messages":[llm_with_tools.invoke(state["messages"])]}
        return chatbot_node
    