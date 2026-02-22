# import os
# from dotenv import load_dotenv
# from google.adk.models.google_llm import Gemini
# from google.adk.sessions import InMemorySessionService
# from google.adk.runners import Runner
# from google.genai import types
# from google.adk.agents import Agent, LlmAgent
# from google.adk.tools import google_search, load_memory, preload_memory
# from matplotlib import text
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# import textwrap
# import asyncio

# """ Try accessing the message according to grok and then encode it to utf-8 before turning it to a pdf"""

# # --- 1. CONFIGURATION ---
# load_dotenv()

# try:
#     GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
#     os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
#     os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
#     print("✅ Gemini API key setup complete.")
# except Exception as e:
#     print(f"🔑 Authentication Error: Check your .env file. Details: {e}")

# # Define helper functions that will be reused throughout the notebook
# async def run_session(
#     runner_instance: Runner, user_queries: list[str] | str, session_id: str = "default"
# ):
#     """Run queries and return the final agent response text (with disclaimer)."""
#     print(f"\n### Session: {session_id}")

#     # Create or retrieve session
#     try:
#         session = await session_service.create_session(
#             app_name=APP_NAME, user_id=USER_ID, session_id=session_id
#         )
#     except:
#         session = await session_service.get_session(
#             app_name=APP_NAME, user_id=USER_ID, session_id=session_id
#         )

#     # Convert single query to list
#     if isinstance(user_queries, str):
#         user_queries = [user_queries]

#     final_text = None

#     # Process each query
#     for query in user_queries:
#         print(f"\nUser > {query}")
#         query_content = types.Content(role="user", parts=[types.Part(text=query)])

#         # Stream agent response
#         async for event in runner_instance.run_async(
#             user_id=USER_ID, session_id=session.id, new_message=query_content
#         ):
#             if event.is_final_response() and event.content and event.content.parts:
#                 part = event.content.parts[0]
#                 if part.text and part.text.strip() != "None":
#                     print(f"Model: > {part.text}")
#                     final_text = part.text
#     return final_text

#     session = await session_service.get_session(APP_NAME, USER_ID, SESSION)
#     agent_last_message = session.state.get("last_agent_response")

#     if agent_last_message:
#         print("From session state:", agent_last_message)
#         save_disclaimer_response_to_pdf(agent_last_message)

# def save_disclaimer_response_to_pdf(text: str, filename="dr_cura_response.pdf"):
#     if not text or not text.strip():
#         print("⚠️ No meaningful text to save -> PDF not created.")
#         return False
#     try:
#         doc = SimpleDocTemplate(filename, pagesize=letter)
#         styles = getSampleStyleSheet()
#         story = []

#         story.append(Paragraph("Dr. Cura Health Assistant Response", styles['Heading1']))
#         story.append(Spacer(1, 12))

#         # Wrap text nicely
#         for line in textwrap.wrap(text, width=90):
#             story.append(Paragraph(line, styles['BodyText']))
#             story.append(Spacer(1, 6))

#         doc.build(story)

#         abs_path = os.path.abspath(filename)
#         file_size_kb = os.path.getsize(filename) / 1024 # in KB
#         print("✅ PDF successfully created")
#         print(f"- Location: {abs_path}")
#         print(f"- Size: {file_size_kb:.1f} KB")
#         return True
#     except Exception as e:
#         print(f"❌ Error creating PDF: {e}")
#         return False

# retry_config = types.HttpRetryOptions(
#     attempts=5,  # Maximum retry attempts
#     exp_base=7,  # Delay multiplier
#     initial_delay=1,
#     http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
# )

# APP_NAME = "CuraOne"  # Application
# USER_ID = "user_01"  # User
# SESSION = "session_001"  # Session

# MODEL_NAME = "gemini-2.5-flash-lite"

# # grok_model = LiteLlm(model="xai/grok-4-1-fast-reasoning",
# #                     api_base = "https://api.x.ai/v1",
# #                     api_key = os.environ["XAI_API_KEY"])

# # --- 2. AGENT SETUP ---
# root_agent = Agent(
#     # model=grok_model,
#     model= Gemini(model="gemini-2.5-flash", retry_options=retry_config),
#     name="health_assistant",
#     description="Interactive clinical reasoning assistant",
#     instruction="""
# You are Dr. Cura, a kind, thorough, and cautious virtual health assistant.
# Your goal is to understand the patient's problem by asking ONE clear question at a time.
# Never give a final diagnosis or treatment plan until you have asked enough questions
# and are confident.

# Rules you MUST follow:
# 1. Always be empathetic and professional.
# 2. Ask exactly ONE question per turn (unless you are ready to summarize).
# 3. If something is unclear, ask for clarification.
# 4. When you think you have enough information, provide:
#    - Generate a well-structured diagnosis report text including:
#         - A summary of the patient's complaints
#         - A short differential diagnosis (most likely → less likely)
#         - Red flags that require immediate ER visit
#         - Recommended next steps (see GP, rest, tests, etc.)
#         - Clear disclaimer at the end
# 5. NEVER prescribe medication or order tests yourself.
# 6. ALWAYS end with the disclaimer:
#    "I am an AI assistant, not a real doctor. This is general information only.
#    Please consult a qualified healthcare professional for proper diagnosis and treatment."

# Start every new conversation with a warm greeting and the first question.
# """.strip(),
#     tools=[google_search],
#     output_key="last_agent_response"
# )

# # Step 2: Set up Session Management
# # InMemorySessionService stores conversations in RAM (temporary)
# session_service = InMemorySessionService()

# # Step 3: Create the Runner
# runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
