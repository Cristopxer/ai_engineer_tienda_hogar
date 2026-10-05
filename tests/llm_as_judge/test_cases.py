import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langsmith import evaluate, Client
from langsmith.evaluation import run_evaluator, EvaluationResult
from langsmith.schemas import Run, Example

from ai_engineer_tienda_hogar.config import Config
from ai_engineer_tienda_hogar.agent.graphs.graph import GraphBuilder
from ai_engineer_tienda_hogar.agent.llms.oai_model import OAIChatModel

load_dotenv(".env", override=True)

os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

EVALUATIONS = []
def create_langsmith_dataset(file_path: str, dataset_name: str) -> str:
    """Reads the JSON file and uploads it to LangSmith as a formal dataset."""
    client = Client()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Check if dataset already exists and delete it so we don't duplicate examples on re-runs
    for ds in client.list_datasets(dataset_name=dataset_name):
        client.delete_dataset(dataset_id=ds.id)
        
    print(f"Creating LangSmith dataset: {dataset_name}...")
    dataset = client.create_dataset(dataset_name=dataset_name)
    
    # Upload examples to LangSmith
    for item in raw_data:
        client.create_example(
            inputs={"user_input": item["user_input"]},
            outputs={"expected_answer": item["expected_answer"]},
            dataset_id=dataset.id
        )
        
    return dataset_name

def build_test_agent():    
    config = Config("src/ai_engineer_tienda_hogar/config.ini")
    graph_builder = GraphBuilder(
        config.get_llm_model(), 
        config.get_text_embedding_model(),
        "src/ai_engineer_tienda_hogar/agent/embeddings/embeddings_db",
        "src/ai_engineer_tienda_hogar/documents/canales_contacto.md"
    )
    return graph_builder.build_graph()

def agent_target_function(inputs: dict) -> dict:
    """Executes the agent and extracts the final text response."""
    agent = build_test_agent()
    
    # LangGraph expects the state as a dictionary
    response = agent.invoke({"messages": [HumanMessage(content=inputs["user_input"])]})
    
    # Extract the final AI response
    final_answer = response["messages"][-1].content
    return {"output": final_answer}


@run_evaluator
def ground_truth_evaluator(run: Run, example: Example) -> EvaluationResult:
    """Evaluates if the agent's answer semantically matches the expected ground truth."""
    
    config = Config("src/ai_engineer_tienda_hogar/config.ini")
    
    judge_llm = OAIChatModel(config.get_llm_model(), 0.0).get_model()
    
    agent_output = run.outputs.get("output", "")
    
    # FIXED: Changed reference_outputs to outputs
    expected_output = example.outputs.get("expected_answer", "")
    user_input = example.inputs.get("user_input", "")

    # Define the judge prompt for Semantic/Ground Truth Evaluation
    judge_prompt = f"""
    You are an expert AI evaluator. Compare the Agent's Answer against the Expected Answer for the User Request.
    Do NOT look for an exact word-for-word match. Focus on semantic correctness.
    Score 1 if the core facts, policies, and actionable details match the Expected Answer. Otherwise, score 0.

    User Request: {user_input}
    Expected Answer: {expected_output}
    Agent's Answer: {agent_output}

    Return ONLY a valid JSON object in the following format:
    {{"score": 1, "reasoning": "Brief explanation here"}}
    """

    # Chain the prompt to the judge LLM
    judgment_response = judge_llm.invoke([HumanMessage(content=judge_prompt)])
    
    # Parse the JSON response securely
    try:
        # Strip potential markdown formatting (e.g., ```json ... ```)
        clean_text = judgment_response.content.strip("`").replace("json\n", "").strip()
        result_data = json.loads(clean_text)
        score = result_data.get("score", 0)
        reasoning = result_data.get("reasoning", "No reasoning provided.")
    except Exception as e:
        score = 0
        reasoning = f"Failed to parse judge JSON. Raw output: {judgment_response.content}"

    EVALUATIONS.append(
    {
        "user_input": user_input,
        "expected_answer": expected_output,
        "agent_answer": agent_output,
        "score": score,
        "reasoning": reasoning,
    })

    return EvaluationResult(
        key="ground_truth_correctness",
        score=score,
        comment=reasoning
    )

def run_evaluation():
    dataset_name = "Tienda Hogar Test Cases"
    
    # 1. Register the dataset in LangSmith
    create_langsmith_dataset("tests/llm_as_judge/test_cases.json", dataset_name)
    
    print("Starting LangSmith evaluation...")
    
    # 2. Run the evaluation by passing the string name of the dataset
    experiment_results = evaluate(
        agent_target_function,
        data=dataset_name,
        evaluators=[ground_truth_evaluator],
        experiment_prefix="tienda_hogar_ground_truth_eval"
    )

    local_df = pd.DataFrame(EVALUATIONS)
    print(f"Pass tests: {len(local_df[local_df['score'] == 1])}/{len(local_df)}")  
    local_df.to_csv("tests/llm_as_judge/results/evaluations.csv", sep=";", index=False)    
    print(f"results saved in tests/llm_as_judge/results/evaluations.csv")    
    return experiment_results

if __name__ == "__main__":    
    run_evaluation()