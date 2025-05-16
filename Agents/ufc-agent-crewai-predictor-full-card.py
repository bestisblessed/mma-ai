import os
import shutil
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, CSVSearchTool
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

### Stuff ###
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
#os.environ["OPENAI_MODEL_NAME"]="gpt-4o"
os.environ["OPENAI_MODEL_NAME"]="gpt-4o-mini"
shutil.rmtree("db", ignore_errors=True)

### Instantiate tools ###
serper_tool = SerperDevTool()
csv_tool1 = CSVSearchTool(csv='./data/event_data_sherdog.csv')
csv_tool2 = CSVSearchTool(csv='./data/fighter_info.csv')

### Fighters and events to predict ###
fight_pairs = [
    ("Gilbert Burns", "Michael Morales"),
    ("Paul Craig", "Rodolfo Bellato"),
    ("Sodiq Yusuff", "Mairon Santos"),
    ("Dustin Stoltzfus", "Nursulton Ruziboev"),
    ("Julian Erosa", "Melquizael Costa"),
    ("Gabriel Green", "Matheus Camilo"),
    ("Jared Gordon", "Thiago Moises"),
    ("Yadier Del  Valle", "Connor Matthews"),
    ("Luana Santos", "Tainara Lisboa"),
    ("Elise Reed", "Denise Gomes"),
    ("Hyun Sung  Park", "Carlos Hernandez"),
    ("Tecia Pennington", "Luana Pinheiro"),
]
base_output_dir = "predictions/ufc-fight-night-256"


### Fight Researcher & Analyst ###
agent1 = Agent(
    role='Fight Researcher & Analyst',
    goal='Gather comprehensive information about upcoming UFC fights',
    backstory="""
    You are a seasoned analyst with a deep understanding of MMA/UFC.
    You specialize in breaking down fights, with expertise in dissecting historical fight outcomes and statistics.
    You provide insights into how a fighter's recent experiences might influence their next performance.
    """,
    tools=[csv_tool1, csv_tool2],
    allow_delegation=True,
    verbose=True,
    max_iter=15
)

### Public Sentiment & News Analyst ###
agent2 = Agent(
    role='Public Sentiment & News Analyst',
    goal='Analyze public bias, sentiment, and unusual news related to the fighters',
    backstory="""
    You are an expert in public sentiment analysis.
    You specialize in gathering and interpreting data from news sources, social media, and other public platforms.
    Your keen insight helps uncover public biases, general sentiment, and any unusual news that might impact the perception of fighters.
    """,
    tools=[serper_tool],
    allow_delegation=True,
    verbose=True,
    max_iter=10
)

### Odds & Market Analyst ###
agent3 = Agent(
    role='Odds & Market Analyst',
    goal='Gather and analyze the latest betting odds and market sentiment for upcoming UFC fights',
    backstory="""
    You are a specialist in sports betting markets and odds analysis.
    You track the latest lines, market movements, and expert predictions to inform fight outcome probabilities.
    """,
    tools=[serper_tool],
    allow_delegation=True,
    verbose=True,
    max_iter=10
)

### Expert MMA Handicapper ###
agent_final = Agent(
    role='Expert MMA Handicapper',
    goal='Generate detailed predictions for upcoming UFC fights based on all gathered data and professional techniques',
    backstory="""
    You are a professional handicapper in Las Vegas.
    You are an expert in predictive analytics and fight analysis.
    You integrate detailed statistics, historical performances, public sentiment, and betting odds to provide a comprehensive prediction for upcoming fights.
    Your insights help forecast the potential outcome with high accuracy.
    """,
    tools=[csv_tool1, csv_tool2, serper_tool],
    allow_delegation=True,
    verbose=True,
    #max_iter=10
)

def to_lower_filename(s):
    return s.lower().replace(" ", "_")

for fighter1, fighter2 in fight_pairs:
    fight_dir = f"{base_output_dir}/{to_lower_filename(fighter1)}_vs_{to_lower_filename(fighter2)}"
    os.makedirs(fight_dir, exist_ok=True)
    task1 = Task(
        description=f"Research detailed statistics and historical performance of {fighter1}.",
        expected_output=f"Comprehensive statistical report on {fighter1}.",
        agent=agent1,
        output_file=f"{fight_dir}/upcoming_fight_research_{to_lower_filename(fighter1)}.md"
    )
    task2 = Task(
        description=f"Research detailed statistics and historical performance of {fighter2}.",
        expected_output=f"Comprehensive statistical report on {fighter2}.",
        agent=agent1,
        output_file=f"{fight_dir}/upcoming_fight_research_{to_lower_filename(fighter2)}.md"
    )
    task3 = Task(
        description=f"Analyze public sentiment, bias, and unusual news about the upcoming fight between {fighter1} and {fighter2}.",
        expected_output=f"Sentiment analysis report on public perception, bias, and unusual news regarding the fight between {fighter1} and {fighter2}.",
        agent=agent2,
        output_file=f"{fight_dir}/upcoming_fight_research_sentiment_{to_lower_filename(fighter1)}_vs_{to_lower_filename(fighter2)}.md"
    )
    task4 = Task(
        description=f"Gather and analyze the latest American betting lines and market sentiment for {fighter1} vs {fighter2}.",
        expected_output="American betting lines for the fight, including moneyline odds for both fighters and method of victory.",
        agent=agent3,
        output_file=f"{fight_dir}/upcoming_fight_research_odds_{to_lower_filename(fighter1)}_vs_{to_lower_filename(fighter2)}.md"
    )
    task_final = Task(
        description=f"Generate a detailed prediction for the upcoming fight between {fighter1} and {fighter2} with a detailed explanation of your reasoning behind it using all gathered information.",
        expected_output="A prediction of the fight outcome with a detailed explanation of your reasoning behind it.",
        agent=agent_final,
        output_file=f"{fight_dir}/upcoming_fight_prediction_{to_lower_filename(fighter1)}_vs_{to_lower_filename(fighter2)}.md"
    )
    crew = Crew(
        agents=[agent1, agent2, agent3, agent_final],
        tasks=[task1, task2, task3, task4, task_final]
    )
    print(f"\nProcessing: {fighter1} vs {fighter2}")
    result = crew.kickoff()
    print(f"Finished: {fighter1} vs {fighter2}\n")
    print("-"*60)