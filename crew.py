import os
from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_groq import ChatGroq
from langchain.agents import Tool
from langchain_community.tools import DuckDuckGoSearchRun

app = Flask(__name__)


# Set up environment variables
os.environ["GROQ_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "970222a7e4512bffc8bfde4705a744f9aec2b355"

# Initialize language model
llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

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
    llm=llm
)

competitor_analyst = Agent(
    role='Competitive Intelligence Analyst',
    goal='Analyze competitors\' strengths and weaknesses, and assess the company\'s current performance',
    backstory="With a background in strategic consulting and competitive intelligence, you excel at dissecting competitor strategies and identifying market opportunities. Your reports have guided numerous companies to success.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=llm
)

content_writer = Agent(
    role='Content Strategist and Copywriter',
    goal='Create an engaging and informative blog post that highlights how the company can stand out',
    backstory="You're a master wordsmith with a knack for crafting compelling narratives. Your content has helped numerous brands establish thought leadership and engage their target audience effectively.",
    verbose=True,
    allow_delegation=True,
    tools=[serp_tool],
    llm=llm
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
    output_file="competitor.txt"
)

content_task = Task(
    description="Using the insights from the research and competitor analysis, write an engaging blog post (800-1000 words) that outlines strategies for the company to stand out in the market. Include specific, actionable advice backed by the research findings.",
    agent=content_writer,
    expected_output="An 800-1000 word blog post with strategies for the company to stand out, incorporating research insights and competitor analysis.",
    output_file="blogpost.pdf"
)

app.route('/crewai', methods=['POST'])
def run_crewai():
    data = request.json
    company_name = data['companyName']
    industry = data['industry']
    main_products = data['mainProducts']

    # Update task descriptions with user input
    research_task.description += f" Focus on the {industry} industry, particularly for companies offering {main_products}."
    competitor_task.description = competitor_task.description.format(company_name=company_name, industry=industry, main_products=main_products)
    content_task.description = content_task.description.format(company_name=company_name, industry=industry, main_products=main_products)

    # Execute the crew's tasks
    crew = Crew(
        agents=[researcher, competitor_analyst, content_writer],
        tasks=[research_task, competitor_task, content_task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()

    return jsonify({
        'research': result[0],
        'competitorAnalysis': result[1],
        'blogPost': result[2]
    })

if __name__ == '__main__':
    app.run(debug=True)
