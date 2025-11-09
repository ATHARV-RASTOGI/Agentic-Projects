from src.states.blogstate import BlogState

class BlogNode:

    def __init__(self,llm):
        self.llm=llm
    
    def title_creation(self,state:BlogState):
        """
        create a title or the blog
        """

        if "topic" in state and state["topic"]:
            prompts="""
                    You are a expeert blog content writter . Use markdown formatting .Generate
                    a blog title for the {topic}. This title should be creative anf SEO friendly. 
                    """
            
            system_message=prompts.format(topic=state["topic"])
            response= self.llm.invoke(system_message)
            return{"blog":{"title":response.content}}
        
    def content_generation(self,state:BlogState):
        if "topic" in state and state["topic"]:
            system_prompt= """ You are a expeert blog content writter . Use markdown formatting .
            Generate a detailed blog content with detailed breakdown fro the {topic}""" 
            system_message= system_prompt.format(topic=state["topic"])
            response=self.llm.invoke(system_message)
            return {"blog":{"title":state['blog']['title'],"content":response.content}}
            
