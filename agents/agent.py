import os
from dotenv import load_dotenv

from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import google_search

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import textwrap

# ─── CONFIG ────────────────────────────────────────────────

load_dotenv()

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
    print("✅ Gemini API key loaded.")
except Exception as e:
    print(f"🔑 Authentication error: {e}")
    exit(1)

# ─── DIAGNOSIS CHECK HELPER ────────────────────────────────

def looks_like_diagnosis_report(text: str) -> bool:
    """
    Returns True if this looks like the final diagnosis/summary message
    (contains the required disclaimer).
    """
    if not text:
        return False
    
    disclaimer_snippet = "I am an AI assistant, not a real doctor"
    return disclaimer_snippet.lower() in text.lower()

# ─── PDF HELPER ────────────────────────────────────────────

def save_disclaimer_response_to_pdf(
    text: str,
    session_id: str = "unknown",
    filename_prefix="dr_cura_diagnosis_"
) -> bool:
    if not text or not text.strip():
        print("⚠️  No text provided → skipping PDF")
        return False

    if not looks_like_diagnosis_report(text):
        print("ℹ️  Response does not contain disclaimer → not saving as diagnosis report")
        return False

    filename = f"{filename_prefix}{session_id}.pdf"

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Dr. Cura – Diagnosis & Recommendations", styles['Heading1']))
        story.append(Spacer(1, 12))

        for line in textwrap.wrap(text, width=90):
            story.append(Paragraph(line, styles['BodyText']))
            story.append(Spacer(1, 6))

        doc.build(story)

        abs_path = os.path.abspath(filename)
        size_kb = os.path.getsize(filename) / 1024
        print("✅ DIAGNOSIS REPORT SAVED AS PDF")
        print(f"   File:   {abs_path}")
        print(f"   Size:   {size_kb:.1f} KB")
        return True

    except Exception as e:
        print(f"❌ PDF creation failed: {e}")
        return False

# ─── RUN HELPER ────────────────────────────────────────────

async def run_session(
    runner: Runner,
    queries: str | list[str],
    session_id: str = "session_001"
) -> str | None:
    APP_NAME = "CuraOne"
    USER_ID = "user_01"

    print(f"\n=== Session: {session_id} ===")

    try:
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:  # noqa: E722
        session = await runner.session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    if isinstance(queries, str):
        queries = [queries]

    last_response = None

    for query in queries:
        print(f"\nUser: {query}")

        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text.strip()
                if text and text != "None":
                    print(f"Dr. Cura:\n{text}\n")
                    last_response = text

                    # Try to save only if it looks like a diagnosis report
                    save_disclaimer_response_to_pdf(last_response, session_id)

    # Final fallback: check session state
    if not last_response or not looks_like_diagnosis_report(last_response):
        session = await runner.session_service.get_session(APP_NAME, USER_ID, session_id)
        state_text = session.state.get("last_agent_response")
        if state_text and looks_like_diagnosis_report(state_text):
            print("\nFound diagnosis report in session.state['last_agent_response']")
            print(state_text)
            save_disclaimer_response_to_pdf(state_text, session_id, "dr_cura_state_")

    return last_response

# ─── MAIN PROGRAM ──────────────────────────────────────────

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

root_agent = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="health_assistant",
    description="Interactive clinical reasoning assistant",
    instruction="""
You are Dr. Cura, a kind, thorough, and cautious virtual health assistant.
Your goal is to understand the patient's problem by asking ONE clear question at a time.
Never give a final diagnosis or treatment plan until you have asked enough questions and are confident.

Rules you MUST follow:
1. Always be empathetic and professional.
2. Ask exactly ONE question per turn (unless you are ready to summarize).
3. If something is unclear, ask for clarification.
4. When you think you have enough information, provide:
   - A summary of the patient's complaints
   - A short differential diagnosis (most likely → less likely)
   - Red flags that require immediate ER visit
   - Recommended next steps (see GP, rest, tests, etc.)
   - Clear disclaimer at the end
5. NEVER prescribe medication or order tests yourself.
6. ALWAYS end with the disclaimer:
   "I am an AI assistant, not a real doctor. This is general information only.
   Please consult a qualified healthcare professional for proper diagnosis and treatment."

Start every new conversation with a warm greeting and the first question.
        """.strip(),
        tools=[google_search],
        output_key="last_agent_response"
    )

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="CuraOne", session_service=session_service)
