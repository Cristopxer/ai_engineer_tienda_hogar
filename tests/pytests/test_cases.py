import os
import json
import pytest
import pandas as pd


from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from ai_engineer_tienda_hogar.config import Config
from ai_engineer_tienda_hogar.agent.graphs.graph import GraphBuilder

load_dotenv(".env", override=True)

os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_ENDPOINT", "")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY", "")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")

RESULTS = []


def build_test_agent():
    config = Config("src/ai_engineer_tienda_hogar/config.ini")
    graph_builder = GraphBuilder(
        config.get_llm_model(),
        config.get_text_embedding_model(),
        "src/ai_engineer_tienda_hogar/agent/embeddings/embeddings_db",
        "src/ai_engineer_tienda_hogar/documents/canales_contacto.md",
    )
    return graph_builder.build_graph()


def load_cases():
    cases_path = Path(__file__).with_name("test_cases.json")
    with open(cases_path, "r", encoding="utf-8") as file:
        return json.load(file)


@pytest.mark.parametrize("case", load_cases())
def test_agent_core_answer_contains_expected_fragment(case):
    agent = build_test_agent()
    result = agent.invoke({"messages": [HumanMessage(content=case["user_input"])]})
    actual_answer = result["messages"][-1].content

    expected_core = case["expected_core"]
    actual_lower = actual_answer.lower()

    if isinstance(expected_core, str):
        expected_cores = [expected_core]
    else:
        expected_cores = list(expected_core)

    passed = any(core.lower() in actual_lower for core in expected_cores)

    RESULTS.append(
        {
            "user_input": case["user_input"],
            "expected_answer": " | ".join(expected_cores),
            "agent_answer": actual_answer,
            "pass": passed,
        }
    )

    assert passed, (
        f"User input: {case['user_input']}\n"
        f"Expected core(s): {expected_cores}\n"
        f"Actual answer: {actual_answer}"
    )

    df = pd.DataFrame(RESULTS, columns=["user_input", "expected_answer", "agent_answer", "pass"])
    Path("tests/pytests/results").mkdir(parents=True, exist_ok=True)
    df.to_csv("tests/pytests/results/evaluations.csv", sep=";", index=False)
