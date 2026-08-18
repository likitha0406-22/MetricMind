from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from pathlib import Path
import pandas as pd
import json
import re


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI()


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# LLM
# =========================================================

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# =========================================================
# LOAD DATASET
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = (
    BASE_DIR
    / "metricmind_dbt"
    / "DATASET"
)

csv_files = list(DATASET_DIR.glob("*.csv"))

df = None


if csv_files:

    try:

        # Load first CSV file
        df = pd.read_csv(csv_files[0])

        print(
            f"Dataset loaded: {csv_files[0].name}"
        )

        print(
            f"Rows: {len(df)}"
        )

        print(
            f"Columns: {list(df.columns)}"
        )

    except Exception as e:

        print(
            "Dataset loading error:",
            e
        )

else:

    print(
        "No CSV dataset found."
    )


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    message: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "MetricMind backend is running"
    }


# =========================================================
# PREPARE DATAFRAME
# =========================================================

def prepare_dataframe(dataframe):

    numeric_columns = [
        "Sales",
        "Profit",
        "Discount",
        "Shipping Cost",
        "Quantity"
    ]

    for column in numeric_columns:

        if column in dataframe.columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

    return dataframe


# =========================================================
# GET AVAILABLE METRICS
# =========================================================

def get_available_metrics():

    if df is None:

        return []

    metrics = [
        "Sales",
        "Profit",
        "Quantity",
        "Discount",
        "Shipping Cost"
    ]

    return [
        column
        for column in metrics
        if column in df.columns
    ]


# =========================================================
# BASIC METRIC ANALYSIS
# =========================================================

def calculate_metric(metric):

    if df is None:

        return None

    if metric not in df.columns:

        return None

    result = df[metric].sum()

    return {
        "metric": metric,
        "total": round(
            float(result),
            2
        )
    }


# =========================================================
# YEAR OVER YEAR ANALYSIS
# =========================================================

def yearly_analysis(metric):

    if df is None:

        return None

    if metric not in df.columns:

        return None

    if "Year" not in df.columns:

        return None

    # Group metric by year
    result = (
        df.groupby("Year")[metric]
        .sum()
        .sort_index()
    )

    # Store yearly values
    values = {}

    for year, value in result.items():

        values[str(year)] = round(
            float(value),
            2
        )

    years = list(result.index)

    comparison = None

    # Need at least two years
    if len(years) >= 2:

        previous_year = years[-2]

        current_year = years[-1]

        previous_value = float(
            result.loc[previous_year]
        )

        current_value = float(
            result.loc[current_year]
        )

        # -----------------------------------------
        # CHANGE
        # -----------------------------------------

        change = (
            current_value
            - previous_value
        )

        # -----------------------------------------
        # DIRECTION
        # -----------------------------------------

        if change > 0:

            direction = "increase"

        elif change < 0:

            direction = "decrease"

        else:

            direction = "no change"

        # -----------------------------------------
        # PERCENTAGE
        # -----------------------------------------

        if previous_value != 0:

            percentage = (
                change
                / previous_value
            ) * 100

        else:

            percentage = None

        comparison = {

            "previous_year": int(
                previous_year
            ),

            "current_year": int(
                current_year
            ),

            "previous_value": round(
                previous_value,
                2
            ),

            "current_value": round(
                current_value,
                2
            ),

            "change": round(
                change,
                2
            ),

            "percentage_change": (
                round(
                    percentage,
                    2
                )
                if percentage is not None
                else None
            ),

            "direction": direction
        }

    return {

        "metric": metric,

        "yearly_values": values,

        "comparison": comparison
    }


# =========================================================
# BREAKDOWN ANALYSIS
# =========================================================

def breakdown_analysis(
    metric,
    dimension
):

    if df is None:

        return None

    if metric not in df.columns:

        return None

    if dimension not in df.columns:

        return None

    result = (
        df.groupby(dimension)[metric]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    output = []

    for name, value in result.items():

        output.append({

            "dimension": str(name),

            "value": round(
                float(value),
                2
            )
        })

    return output


# =========================================================
# YEAR + DIMENSION ANALYSIS
# =========================================================

def year_dimension_analysis(
    metric,
    dimension
):

    if df is None:

        return None

    if metric not in df.columns:

        return None

    if dimension not in df.columns:

        return None

    if "Year" not in df.columns:

        return None

    # Group by Year + Dimension
    result = (
        df.groupby(
            ["Year", dimension]
        )[metric]
        .sum()
        .reset_index()
    )

    years = sorted(
        result["Year"].unique()
    )

    # Not enough years
    if len(years) < 2:

        return result.to_dict(
            orient="records"
        )

    previous_year = years[-2]

    current_year = years[-1]

    # Previous year
    previous = (
        result[
            result["Year"]
            == previous_year
        ]
        .set_index(dimension)[metric]
    )

    # Current year
    current = (
        result[
            result["Year"]
            == current_year
        ]
        .set_index(dimension)[metric]
    )

    # All dimensions
    all_dimensions = (
        set(previous.index)
        | set(current.index)
    )

    output = []

    for name in all_dimensions:

        previous_value = float(
            previous.get(
                name,
                0
            )
        )

        current_value = float(
            current.get(
                name,
                0
            )
        )

        change = (
            current_value
            - previous_value
        )

        output.append({

            "dimension": str(name),

            "previous_year": int(
                previous_year
            ),

            "current_year": int(
                current_year
            ),

            "previous_value": round(
                previous_value,
                2
            ),

            "current_value": round(
                current_value,
                2
            ),

            "change": round(
                change,
                2
            )
        })

    # Smallest decrease -> largest increase
    output.sort(
        key=lambda x: x["change"]
    )

    return output


# =========================================================
# LLM ANALYSIS PLAN
# =========================================================

def get_analysis_plan(question):

    metrics = get_available_metrics()

    prompt = f"""
You are the analysis planner for MetricMind.

Available metrics:
{metrics}

Available dimensions:
Region
Category
Sub Category
Segment
Country
Market
Year

User question:
{question}

Determine the metric required.

Return ONLY valid JSON.

Use exactly this format:

{{
    "metric": "Sales",
    "needs_year_comparison": true,
    "needs_region_analysis": true,
    "needs_category_analysis": true,
    "needs_factor_analysis": true
}}

Rules:

1. If the question mentions sales, use Sales.
2. If the question mentions profit, use Profit.
3. If the question mentions quantity, use Quantity.
4. If the question mentions discount, use Discount.
5. If the question mentions shipping cost, use Shipping Cost.
6. For "why did profit change", use Profit.
7. Do not invent metrics.
"""

    try:

        response = llm.invoke(prompt)

        text = response.content.strip()

        # Find JSON
        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:

            return json.loads(
                match.group()
            )

    except Exception as e:

        print(
            "Planning error:",
            e
        )

    # =====================================================
    # SAFE FALLBACK
    # =====================================================

    question_lower = (
        question.lower()
    )

    metric = "Sales"

    if "profit" in question_lower:

        metric = "Profit"

    elif "quantity" in question_lower:

        metric = "Quantity"

    elif "discount" in question_lower:

        metric = "Discount"

    elif (
        "shipping" in question_lower
        or "shipping cost" in question_lower
    ):

        metric = "Shipping Cost"

    elif "sales" in question_lower:

        metric = "Sales"

    return {

        "metric": metric,

        "needs_year_comparison": True,

        "needs_region_analysis": True,

        "needs_category_analysis": True,

        "needs_factor_analysis": True
    }


# =========================================================
# FINAL ANSWER GENERATION
# =========================================================

def generate_final_answer(
    question,
    analysis
):

    # -----------------------------------------------------
    # Extract overall comparison
    # -----------------------------------------------------

    overall = analysis.get(
        "step_1_overall"
    )

    comparison = None

    if overall:

        comparison = overall.get(
            "comparison"
        )

    # -----------------------------------------------------
    # If no comparison
    # -----------------------------------------------------

    if not comparison:

        return (
            "There is not enough yearly data "
            "to calculate a year-over-year comparison."
        )

    previous_year = comparison[
        "previous_year"
    ]

    current_year = comparison[
        "current_year"
    ]

    previous_value = comparison[
        "previous_value"
    ]

    current_value = comparison[
        "current_value"
    ]

    change = comparison[
        "change"
    ]

    percentage = comparison[
        "percentage_change"
    ]

    direction = comparison[
        "direction"
    ]

    metric = analysis[
        "metric"
    ]

    # -----------------------------------------------------
    # Region analysis
    # -----------------------------------------------------

    regions = analysis.get(
        "step_2_region",
        []
    )

    largest_region_increase = None

    largest_region_decrease = None

    if regions:

        largest_region_increase = max(
            regions,
            key=lambda x: x["change"]
        )

        largest_region_decrease = min(
            regions,
            key=lambda x: x["change"]
        )

    # -----------------------------------------------------
    # Category analysis
    # -----------------------------------------------------

    categories = analysis.get(
        "step_3_category",
        []
    )

    largest_category_increase = None

    largest_category_decrease = None

    if categories:

        largest_category_increase = max(
            categories,
            key=lambda x: x["change"]
        )

        largest_category_decrease = min(
            categories,
            key=lambda x: x["change"]
        )

    # -----------------------------------------------------
    # FACTORS
    # -----------------------------------------------------

    factors = analysis.get(
        "step_4_factors",
        {}
    )

    # -----------------------------------------------------
    # Build LLM prompt
    # -----------------------------------------------------

    prompt = f"""
You are the final answer generator for MetricMind.

USER QUESTION:
{question}

IMPORTANT:
The user may make an incorrect assumption.

For example:
User: "Why did profit decrease?"
But the data may show that profit increased.

In that case you MUST correct the user.

==================================================
CALCULATED OVERALL RESULT
==================================================

Metric: {metric}

Previous year: {previous_year}
Current year: {current_year}

Previous value: {previous_value}
Current value: {current_value}

Change: {change}

Percentage change: {percentage}%

Direction: {direction}

==================================================
REGION ANALYSIS
==================================================

Largest region increase:
{json.dumps(largest_region_increase, indent=2)}

Largest region decrease:
{json.dumps(largest_region_decrease, indent=2)}

==================================================
CATEGORY ANALYSIS
==================================================

Largest category increase:
{json.dumps(largest_category_increase, indent=2)}

Largest category decrease:
{json.dumps(largest_category_decrease, indent=2)}

==================================================
FACTORS
==================================================

{json.dumps(factors, indent=2)}

==================================================
STRICT RULES
==================================================

1. Use ONLY the calculated data above.

2. Never invent numbers.

3. Never change any number.

4. Never change the direction.

5. The official direction is:
   {direction}

6. If direction is "increase", say that the metric increased.

7. If direction is "decrease", say that the metric decreased.

8. If the user assumes the wrong direction, explicitly correct them.

9. For example, if the user asks:
   "Why did profit decrease?"
   and direction is "increase",
   say:
   "Profit did not decrease. It increased..."

10. For region analysis, use the actual largest increase/decrease
    values provided above.

11. For category analysis, use the actual largest increase/decrease
    values provided above.

12. Do not guess which region or category is largest.

13. Do not claim causation unless the data directly proves it.

14. When discussing possible factors, use:
    "may have contributed"
    rather than claiming definite causation.

15. Do not call a factor stable unless its values are actually
    unchanged.

16. Do not compare unrelated years.

17. Use only {previous_year} and {current_year} for the
    year-over-year comparison.

18. Keep the answer concise and easy to understand.

19. Do not expose internal reasoning.

20. Do not mention prompts, analysis steps, LLMs, or hidden reasoning.

21. Do not say "I am MetricMind".

Return only the final answer.
"""

    try:

        response = llm.invoke(
            prompt
        )

        return response.content.strip()

    except Exception as e:

        print(
            "Final answer generation error:",
            e
        )

        # -------------------------------------------------
        # Deterministic fallback
        # -------------------------------------------------

        if direction == "increase":

            return (
                f"{metric} did not decrease. "
                f"It increased from "
                f"{previous_value:,.2f} in "
                f"{previous_year} to "
                f"{current_value:,.2f} in "
                f"{current_year}, "
                f"an increase of "
                f"{abs(change):,.2f} "
                f"({abs(percentage):.2f}%)."
            )

        elif direction == "decrease":

            return (
                f"{metric} decreased from "
                f"{previous_value:,.2f} in "
                f"{previous_year} to "
                f"{current_value:,.2f} in "
                f"{current_year}, "
                f"a decrease of "
                f"{abs(change):,.2f} "
                f"({abs(percentage):.2f}%)."
            )

        else:

            return (
                f"{metric} showed no change between "
                f"{previous_year} and "
                f"{current_year}."
            )


# =========================================================
# MULTI-STEP ANALYSIS
# =========================================================

def perform_multi_step_analysis(
    question
):

    if df is None:

        return {
            "error": "Dataset is not available."
        }

    # Prepare numeric columns
    prepare_dataframe(df)

    # =====================================================
    # STEP 1: ANALYSIS PLAN
    # =====================================================

    plan = get_analysis_plan(
        question
    )

    metric = plan.get(
        "metric",
        "Sales"
    )

    if metric not in df.columns:

        metric = "Sales"

    analysis = {

        "question": question,

        "metric": metric,

        "available_metrics":
            get_available_metrics(),

        "analysis_steps": []
    }

    # =====================================================
    # STEP 2: OVERALL YEAR ANALYSIS
    # =====================================================

    yearly = yearly_analysis(
        metric
    )

    analysis[
        "step_1_overall"
    ] = yearly

    analysis[
        "analysis_steps"
    ].append(
        "Overall year comparison"
    )

    # =====================================================
    # QUESTION TYPE
    # =====================================================

    question_lower = (
        question.lower()
    )

    why_question = (
        "why" in question_lower
        or "reason" in question_lower
        or "factor" in question_lower
        or "caused" in question_lower
        or "affect" in question_lower
    )

    # =====================================================
    # WHY QUESTIONS
    # =====================================================

    if why_question:

        # -------------------------------------------------
        # REGION
        # -------------------------------------------------

        region_result = (
            year_dimension_analysis(
                metric,
                "Region"
            )
        )

        analysis[
            "step_2_region"
        ] = region_result

        analysis[
            "analysis_steps"
        ].append(
            "Region breakdown"
        )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        category_result = (
            year_dimension_analysis(
                metric,
                "Category"
            )
        )

        analysis[
            "step_3_category"
        ] = category_result

        analysis[
            "analysis_steps"
        ].append(
            "Category breakdown"
        )

        # -------------------------------------------------
        # FACTORS
        # -------------------------------------------------

        factors = {}

        # Discount
        if (
            "Discount" in df.columns
            and "Year" in df.columns
        ):

            discount = (
                df.groupby("Year")[
                    "Discount"
                ]
                .mean()
                .round(2)
                .to_dict()
            )

            factors[
                "discount"
            ] = {
                str(k): float(v)
                for k, v in discount.items()
            }

        # Shipping cost
        if (
            "Shipping Cost" in df.columns
            and "Year" in df.columns
        ):

            shipping = (
                df.groupby("Year")[
                    "Shipping Cost"
                ]
                .sum()
                .round(2)
                .to_dict()
            )

            factors[
                "shipping_cost"
            ] = {
                str(k): float(v)
                for k, v in shipping.items()
            }

        # Quantity
        if (
            "Quantity" in df.columns
            and "Year" in df.columns
        ):

            quantity = (
                df.groupby("Year")[
                    "Quantity"
                ]
                .sum()
                .round(2)
                .to_dict()
            )

            factors[
                "quantity"
            ] = {
                str(k): float(v)
                for k, v in quantity.items()
            }

        analysis[
            "step_4_factors"
        ] = factors

        analysis[
            "analysis_steps"
        ].append(
            "Factor analysis"
        )

    # =====================================================
    # REGION QUESTIONS
    # =====================================================

    elif (
        "region" in question_lower
        or "area" in question_lower
    ):

        region_result = (
            year_dimension_analysis(
                metric,
                "Region"
            )
        )

        analysis[
            "step_2_region"
        ] = region_result

        analysis[
            "analysis_steps"
        ].append(
            "Region breakdown"
        )

    # =====================================================
    # CATEGORY QUESTIONS
    # =====================================================

    elif (
        "category" in question_lower
        or "product category"
        in question_lower
    ):

        category_result = (
            year_dimension_analysis(
                metric,
                "Category"
            )
        )

        analysis[
            "step_3_category"
        ] = category_result

        analysis[
            "analysis_steps"
        ].append(
            "Category breakdown"
        )

    return analysis


# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    user_message = (
        request.message.strip()
    )

    if not user_message:

        return {
            "reply": "Please enter a question."
        }

    try:

        # -----------------------------------------------
        # Perform data analysis
        # -----------------------------------------------

        analysis = (
            perform_multi_step_analysis(
                user_message
            )
        )

        if "error" in analysis:

            return {
                "reply":
                    analysis["error"]
            }

        # -----------------------------------------------
        # Generate final answer
        # -----------------------------------------------

        final_answer = (
            generate_final_answer(
                user_message,
                analysis
            )
        )

        return {

            "reply": final_answer,

            "analysis": analysis
        }

    except Exception as e:

        print(
            "Chat error:",
            e
        )

        return {

            "reply":
                f"Unable to process the request: {str(e)}"
        }


# =========================================================
# RUN
# =========================================================

# Start with:
#
# python -m uvicorn backend.main:app --reload
#
# because main.py is inside the backend folder.