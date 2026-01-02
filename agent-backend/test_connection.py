# """
# Simple test to verify LangGraph + Groq integration works
# Run: python test_langgraph_groq.py
# """

# import os
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph, MessagesState, START, END

# # Load environment variables
# load_dotenv()

# print("=" * 60)
# print("Testing LangGraph + Groq Integration")
# print("=" * 60)

# # Step 1: Initialize Groq LLM
# print("\n1. Initializing Groq LLM...")
# try:
#     llm = ChatGroq(
#         model=os.getenv("MODEL_NAME"),
#         api_key=os.getenv("GROQ_API_KEY"),
#         temperature=0.7
#     )
#     print(f"✅ Groq LLM initialized: {os.getenv('MODEL_NAME')}")
# except Exception as e:
#     print(f"❌ Failed to initialize Groq: {e}")
#     exit(1)

# # Step 2: Test simple LLM call (without graph)
# print("\n2. Testing simple LLM call...")
# try:
#     response = llm.invoke("Say 'Hello from LangChain' in one sentence")
#     print(f"✅ LLM Response: {response.content}")
# except Exception as e:
#     print(f"❌ LLM call failed: {e}")
#     exit(1)

# # Step 3: Create simple agent node
# print("\n3. Creating agent node...")
# def agent_node(state: MessagesState):
#     """Simple agent that calls the LLM"""
#     response = llm.invoke(state["messages"])
#     return {"messages": [response]}

# print("✅ Agent node created")

# # Step 4: Build LangGraph
# print("\n4. Building LangGraph...")
# try:
#     graph = StateGraph(MessagesState)
#     graph.add_node("agent", agent_node)
#     graph.add_edge(START, "agent")
#     graph.add_edge("agent", END)
#     app = graph.compile()
#     print("✅ LangGraph compiled successfully")
# except Exception as e:
#     print(f"❌ Graph compilation failed: {e}")
#     exit(1)

# # Step 5: Test the graph
# print("\n5. Testing LangGraph execution...")
# try:
#     test_input = {"messages": [("user", "Generate a simple Python hello world script")]}
#     result = app.invoke(test_input)
    
#     # Extract response
#     final_message = result["messages"][-1].content
    
#     print("✅ LangGraph execution successful!")
#     print("\n" + "=" * 60)
#     print("AGENT RESPONSE:")
#     print("=" * 60)
#     print(final_message)
#     print("=" * 60)
    
# except Exception as e:
#     print(f"❌ Graph execution failed: {e}")
#     exit(1)

# print("\n✅ ALL TESTS PASSED!")
# print("LangGraph + Groq integration is working correctly.")
# print("=" * 60)