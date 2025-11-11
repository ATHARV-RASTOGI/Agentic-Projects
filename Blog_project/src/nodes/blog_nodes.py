from src.states.blogstate import BlogState
from langchain_core.messages import HumanMessage,SystemMessage
from src.states.blogstate import Blog


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
    
    def translate(self, state: BlogState):
        """
        Translate the content to the specified language.
        """
        translation_prompt = """
        Translate the following content into {current_language}.
        - Maintain the original tone, style, and formatting.
        - Adapt cultural references and idioms to be appropriate for {current_language}.
    
        ORIGINAL CONTENT:
        {blog_content}

        Return only the translated content, nothing else.
    """
    
        blog_content = state["blog"]["content"]
    
        formatted_prompt = translation_prompt.format(
            current_language=state["current_language"],
            blog_content=blog_content
        )
    
        # Use regular invoke - NO with_structured_output
        response = self.llm.invoke(formatted_prompt)
    
        return {
            "blog": {
                "title": state["blog"]["title"],
                "content": response.content  # Just use response.content directly
            },
            "current_language": state["current_language"]
        }
    # def translate(self,state:BlogState):
    #     """
    #     Translate the content to the specified language.
    #     """
    #     translation_prompt="""
    #     Translate the following content into {current_language}.
    #     - Maintain the original tone, style, and formatting.
    #     - Adapt cultural references and idioms to be appropriate for {current_language}.

    #     ORIGINAL CONTENT:
    #     {blog_content}

    #     """

    #     blog_content=state["blog"]["content"]
    #     messages=[
    #         HumanMessage(translation_prompt.format(current_language=state["current_language"],blog_content=blog_content))
    #     ]
    #     translation_content=self.llm.with_structured_output(Blog).invoke(messages)

    #     return {
    #     "blog": {
    #         "title": state["blog"]["title"],
    #         "content": response.content  # Access the content from the response
    #     },
    #     "current_language": state["current_language"]
    # }
    
    def route(self,state:BlogState):
        return{"current_language":state['current_language']}
    
    def route_decision(self,state:BlogState):
        """
        Route the content to the respective translation function.
        """

        if state["current_language"]=="japanese":
            return "japanese"
        elif state["current_language"]=="hindi":
            return "hindi"
        else:
            return state['current_language']