#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from agents.crew import InnobidAiAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs ={
            'bidData': ' {"bid_id": 1, "amount": 15000, "completion_time": "2023-12-31T23:59:59Z", "technical_proposal": "Proposal for advanced software development.", "vendor_experience": "5 years in software development.", "submission_date": "2023-10-01T12:00:00Z", "status": "submitted", "documents": [{"id": 101, "name": "Technical Proposal Document", "url": "./The Ultimate Checklist for Adopting AI at Work (Spotlight Update).pdf", "type": "pdf"}, {"id": 102, "name": "Vendor Experience Document", "url": "./Linkedin Profile.pdf", "type": "pdf"}], "bidder": {"id": 201, "name": "John Doe", "company": "Doe Enterprises", "experience": "10 years in the industry"}, "tender": {"id": 301, "title": "Software Development Tender", "description": "Tender for developing a new software application.", "budget": 20000, "requirements": ["Requirement 1: User authentication", "Requirement 2: Data encryption"]}}'
        }
    
    try:
        InnobidAiAgent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        InnobidAiAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        InnobidAiAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        InnobidAiAgent().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
