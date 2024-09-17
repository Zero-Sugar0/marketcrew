import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool
from langchain_community.tools import DuckDuckGoSearchRun

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
load_dotenv()

# Set up environment variables
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize language model
llmq = ChatGroq(
    model_name="mixtral-8x7b-32768",
    max_tokens=32768,
    top_p=1,
    stream=True,
    stop=None
    )


llmg = ChatGoogleGenerativeAI(
    temperature=1, 
    model="models/gemini-1.5-flash",
    top_k=64,
    top_p=1
    )

# Initialize search tool
search_tool = DuckDuckGoSearchRun()
serp_tool = SerperDevTool(n_results=3)
tool = ScrapeWebsiteTool(website_url='https://www.example.com')

# Define agents
researcher = Agent(
    role='Market Research Specialist',
    goal='Conduct deep research on the company, industry trends, and competitors',
    backstory="You're a seasoned market researcher with 15 years of experience in various industries. Your analytical skills and attention to detail are unparalleled, allowing you to uncover insights that others might miss.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=llmg
)

competitor_analyst = Agent(
    role='Competitive Intelligence Analyst',
    goal='Analyze competitors\' strengths and weaknesses, and assess the company\'s current performance',
    backstory="With a background in strategic consulting and competitive intelligence, you excel at dissecting competitor strategies and identifying market opportunities. Your reports have guided numerous companies to success.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=llmq
)

content_writer = Agent(
    role='Content Strategist and Copywriter',
    goal='Create an engaging and informative blog post that highlights how the company can stand out',
    backstory="You're a master wordsmith with a knack for crafting compelling narratives. Your content has helped numerous brands establish thought leadership and engage their target audience effectively.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=llmg
)

# Define tasks
research_task = Task(
    description="Conduct comprehensive research on the company's industry, focusing on current trends, challenges, and opportunities. Identify key factors that contribute to success in this market.",
    agent=researcher,
    expected_output="A detailed report on industry trends, challenges, and opportunities, with key success factors.",
    output_file="reaserch.md"
)

competitor_task = Task(
    description="Analyze the top 3-5 competitors in the industry. Identify their strengths, weaknesses, and unique selling propositions. Also, assess our company's current performance and market position.",
    agent=competitor_analyst,
    expected_output="A comprehensive analysis of competitors' strengths and weaknesses, and our company's current market position.",
    output_file="competitor.md"
)

content_task = Task(
    description="Using the insights from the research and competitor analysis, write an engaging blog post (800-1000 words) that outlines strategies for the company to stand out in the market. Include specific, actionable advice backed by the research findings.",
    agent=content_writer,
    expected_output="An 800-1000 word blog post with strategies for the company to stand out, incorporating research insights and competitor analysis.",
    output_file="blogpost.pdf"
)

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/agents')
def agents():
    return render_template('agents.html')
    
    # Flask-SocketIO event to start the agents
@socketio.on('start_agents')
def start_agents(data):
    company_name = data['companyName']
    industry = data['industry']
    main_products = data['mainProducts']

    # Customize tasks based on user input
    research_task.description += f" Focus on the {industry} industry and companies offering {main_products}."
    competitor_task.description += f" Analyze competitors in the {industry} industry for {main_products}."


    # Execute the crew's tasks
    crew = Crew(
        agents=[researcher, competitor_analyst, content_writer],
        tasks=[research_task, competitor_task, content_task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()


    # Emit results back to the frontend
    socketio.emit('researcher_output', "Starting research...")
    # Run researcher task
    socketio.emit('competitor_analyst_output', "Starting competitor analysis...")
    # Run competitor analyst task
    socketio.emit('content_writer_output', "Starting content writing...")
    # Run content writer task

    # After all tasks are complete
    socketio.emit('agents_complete')

# Run the app with Flask-SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True)
