import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message
        print(user_message)
        
        if usecase == "Basic Chatbot":
            for event in graph.stream({'messages': ("user", user_message)}):
                print(event.values())
                for value in event.values():
                    print(value['messages'])
                    with st.chat_message("user"):
                        st.write(user_message)
                    with st.chat_message("assistant"):
                        st.write(value["messages"].content)
        
        elif usecase == "Advanced Chat-Bot":
            # Display user message first
            with st.chat_message("user"):
                st.write(user_message)
            
            # Prepare state and invoke the graph
            initial_state = {"messages": [HumanMessage(content=user_message)]}
            res = graph.invoke(initial_state)
            
            # Process all messages in the response
            for message in res["messages"]:
                # Skip the initial user message (already displayed)
                if isinstance(message, HumanMessage):
                    continue
                    
                elif isinstance(message, ToolMessage):
                    with st.chat_message("ai"):
                        st.write("🔧 Tool Start")
                        st.json(message.content if isinstance(message.content, dict) else {"result": message.content})
                        st.write("Tool Call End")
                        
                elif isinstance(message, AIMessage):
                    # Check if it's a tool call or regular response
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        with st.chat_message("assistant"):
                            st.write(f"🔍 Calling tool: {message.tool_calls[0]['name']}")
                    elif message.content:
                        with st.chat_message("assistant"):
                            st.write(message.content)

        elif usecase == "AI News":
            frequency = self.user_message.lower()
            with st.spinner('Fetching and summarizing news...'):
                result = graph.invoke({"messages": [HumanMessage(content=frequency)]})
                try:
                    # Read the markdown file
                    AI_NEWS_PATH = f"./News/{frequency}_summary.md"
                    with open(AI_NEWS_PATH, "r", encoding="utf-8") as file:
                        markdown_content = file.read()
        
                    # Display the markdown content in streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")