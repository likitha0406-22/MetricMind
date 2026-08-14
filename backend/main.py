from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from pathlib import Path
import pandas as pd

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Ollama / LangChain
# -----------------------------
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)

# -----------------------------
# Load MetricMind dataset
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "metricmind_dbt" / "DATASET"

csv_files = list(DATASET_DIR.glob("*.csv"))

df = None

if csv_files:
    try:
        df = pd.read_csv(csv_files[0])
        print(f"Dataset loaded: {csv_files[0].name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print("Dataset loading error:", e)
else:
    print("No CSV dataset found.")


# -----------------------------
# Request model
# -----------------------------
class ChatRequest(BaseModel):
    message: str


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "MetricMind backend is running"
    }


# -----------------------------
# Chat
# -----------------------------
@app.post("/chat")
async def chat(request: ChatRequest):

    user_message = request.message

    # Create dataset context
    if df is not None:

        dataset_info = f"""
Dataset information:

Number of rows: {len(df)}

Columns:
{", ".join(df.columns.astype(str))}

First 5 rows:
{df.head().to_string(index=False)}

Basic statistics:
{df.describe(include="all").to_string()}
"""

    else:
        dataset_info = "No dataset is currently available."

    # System instructions for MetricMind AI
    prompt = f"""
You are the AI assistant of MetricMind.

MetricMind is a data analytics platform.

Your role is to help users understand their datasets,
identify trends, explain metrics, and provide useful
data-driven insights.

IMPORTANT IDENTITY RULE:
You are the AI assistant OF MetricMind.
Do not say "I am MetricMind."
If asked who you are, say that you are the AI assistant
of MetricMind.

Use the dataset information provided below when answering
questions related to the data.

Do not invent numbers or facts that are not supported
by the available dataset.

If the dataset does not contain enough information to
answer a question, clearly say so.

Dataset context:
{dataset_info}

User question:
{user_message}

Provide a clear and concise answer.
"""

    try:
        response = llm.invoke(prompt)

        return {
            "reply": response.content
        }

    except Exception as e:
        return {
            "reply": f"Unable to process the request: {str(e)}"
        }