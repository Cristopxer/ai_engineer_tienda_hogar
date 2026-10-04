import json
from pathlib import Path

from langchain.tools import tool

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"


@tool
def consultar_estado_pedido(order_id: str) -> dict:
    """
    Search an order by its ID in the mock orders table.

    Args:
        order_id (str): The unique order identifier (e.g., ORD-1001).

    Returns:
        dict: The order details if found, or {"estado": "no encontrado"} if it doesn't exist.
    """
    if not ORDERS_FILE.exists():
        return {"error": f"Orders file not found at {ORDERS_FILE}"}

    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders_data = json.load(f)

    for order in orders_data:
        if order["order_id"].lower() == order_id.lower():
            return order

    return {"estado": "no encontrado"}
