# ------------------------------------------------------------------------------
# 1. EXTERNAL/NON-USUAL IMPORTS & SYSTEM CONFIGURATION
# ------------------------------------------------------------------------------
import os   # Python's built-in operating system module.
            # Needed to directly inspect/modify environment variables in memory.

from dotenv import load_dotenv  
# NON-USUAL BEHAVIOR: 
# By default, Python does NOT automatically read files named ".env". 
# load_dotenv() manually parses your .env file and injects variables like 
# ANTHROPIC_API_KEY into os.environ so third-party packages can see them.
load_dotenv()

# EXTERNAL WORKAROUND (BYPASSING CREWAI'S OPENAI DEFAULT):
# CrewAI relies heavily on OpenAI as its default provider engine. 
# Even if you tell your Agents to use Claude, lower-level background subsystems 
# check for an OpenAI key on startup. 
# Setting "OPENAI_API_KEY" to a placeholder ("NA") prevents CrewAI from crashing 
# with an "OPENAI_API_KEY is required" error before your Claude code executes.
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, Process, LLM

# ------------------------------------------------------------------------------
# 2. LLM INITIALIZATION
# ------------------------------------------------------------------------------
# NOTE: claude-3-5-sonnet-latest has been retired (404s on this key).
# Use a currently available model, e.g. "anthropic/claude-sonnet-5".
# `temperature` is deprecated/unsupported for this model, so it's omitted.
claude_llm = LLM(
    model="anthropic/claude-sonnet-5"
)

# ------------------------------------------------------------------------------
# 3. AGENT DEFINITIONS
# ------------------------------------------------------------------------------
# EXTERNAL REQUIREMENT (EXPLICIT LLM ASSIGNMENT):
# CrewAI Agents do NOT inherit global LLM instances automatically.
# Explicitly passing `llm=claude_llm` ensures these agents call Claude instead of OpenAI.
researcher = Agent(
    role="Tech Trends Researcher",
    goal="Find breakthrough developments in artificial intelligence.",
    backstory="You are a veteran technology analyst who loves uncovering key industry trends.",
    llm=claude_llm,  # Explicitly override the OpenAI fallback
    verbose=True
)

writer = Agent(
    role="Technical Content Writer",
    goal="Craft clear, non-technical summaries of technical research.",
    backstory="You are a skilled science journalist capable of turning complex research into engaging bullet points.",
    llm=claude_llm,  # Explicitly override the OpenAI fallback
    verbose=True
)

# ------------------------------------------------------------------------------
# 4. TASK DEFINITIONS
# ------------------------------------------------------------------------------
research_task = Task(
    description="Identify the top 3 developments in AI multi-agent systems this year.",
    expected_output="A bulleted list of 3 key AI agent advancements with brief descriptions.",
    agent=researcher
)

writing_task = Task(
    description="Take the research report and write a concise summary suitable for a business newsletter.",
    expected_output="A 2-paragraph summary highlighting why these AI agent trends matter.",
    agent=writer
)

# ------------------------------------------------------------------------------
# 5. CREW CONTAINER & EXECUTION
# ------------------------------------------------------------------------------
# FIX: Removed `llm=claude_llm` from Crew configuration. 
# In standard sequential crews, individual agents execute tasks using their assigned LLMs.
tech_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential  # Sequentially pipes Task 1's text output as input to Task 2
)

result = tech_crew.kickoff()

print("\n--- FINAL WORKFLOW RESULT ---")
print(result)
