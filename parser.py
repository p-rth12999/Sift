import json
from ollama import chat
from pydantic import BaseModel, Field

class OrderExtraction(BaseModel):
    customer_name: str = Field(description="Customer's full name, or 'Unknown' if not provided")
    phone_number: str = Field(description="10-digit phone/mobile number, or 'Unknown'")
    item_name: str = Field(description="Name and color of the product ordered")
    quantity: int = Field(description="Number of units ordered, default to 1")
    size: str = Field(description="Clothing/item size like S, M, L, XL, Free Size, or 'N/A'")
    total_amount: float = Field(description="Total price paid or mentioned in INR, default to 0.0")
    payment_status: str = Field(description="Strictly 'Paid', 'COD', or 'Pending'")
    delivery_address: str = Field(description="Complete street/flat delivery address")

SYSTEM_PROMPT = """
You are Sift, an expert Indian e-commerce order extraction engine for Instagram & WhatsApp sellers.
You understand English, Hindi, and Hinglish (e.g., 'bhej do', 'kar diya GPay', 'pehenne wala', 'kal tak').

Rules:
1. Extract order details accurately from the messy chat text into the JSON schema.
2. If the user mentions 'GPay', 'PhonePe', 'Paytm', 'UPI done', or 'paid', set payment_status to 'Paid'.
3. If the user mentions 'Cash on delivery' or 'COD', set payment_status to 'COD'. Otherwise set 'Pending'.
4. If any string field is missing, set it to 'Unknown'.
"""

def parse_hinglish_dm(raw_text: str, model_name: str = "llama3.2:3b") -> dict:
    response = chat(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract the order from this DM:\n\n{raw_text}"}
        ],
        format=OrderExtraction.model_json_schema(),
        options={"temperature": 0.0}
    )
    return json.loads(response.message.content)
