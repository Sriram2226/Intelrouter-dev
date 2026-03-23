# Project Overview: IntelRouter

IntelRouter is an intelligent API gateway designed to optimize LLM (Large Language Model) usage by routing user queries to different models based on their complexity and cost constraints.

## 🚀 What the Project Does

IntelRouter acts as a middle layer between users and multiple LLMs. It:
1.  **Analyzes** incoming user queries for complexity.
2.  **Routes** queries to the most appropriate model (e.g., GPT-4o-mini for simple tasks, more powerful models for complex ones).
3.  **Manages Costs** by ensuring premium models are only used when necessary.
4.  **Provides a Dashboard** for monitoring usage, costs, and routing performance.

## 🛠️ How it Works

The project uses a **Hybrid Routing System** that combines machine learning and rule-based logic.

### 1. Hybrid Router Flow
When a query arrives, the `route_query` function (`app/router/hybrid_router.py`) handles the decision:
-   **User Overrides:** If a user specifies a difficulty (EASY/MEDIUM/HARD), it is honored immediately.
-   **ML Classifier (Primary):** The query is sent to a Logistic Regression model that predicts the difficulty.
-   **Algorithmic Scorer (Fallback):** If the ML model is "UNCERTAIN", a rule-based scorer uses keyword matching (e.g., looking for "reasoning", "system design", "code") to determine complexity.

### 2. Machine Learning Pipeline
The ML system (`app/ml`) is built for continuous improvement:
-   **Feature Extraction:** Extracts text statistics (length, word count), POS tags, and TF-IDF features.
-   **Model Storage:** Models are stored in Supabase Storage and loaded dynamically at startup.
-   **Automated Retraining:** A GitHub Action triggers every 30 days to retrain the model on user feedback (`ml_data` table).

### 3. Core Components
-   **`app/main.py`:** FastAPI entry point with request/response logging and CORS configuration.
-   **`app/api/`:** Contains endpoints for queries, user dashboards, and admin metrics.
-   **`app/llm/`:** Handles integration with different LLM providers via Hugging Face and OpenAI.
-   **`frontend/`:** A modern React dashboard for users and admins.

## ✨ Key Capabilities

-   **Dynamic Routing:** Automatically chooses between models like `gpt-4o-mini` and `gpt-4o`.
-   **Real-time Usage Tracking:** Monitors daily token limits and costs.
-   **Admin Suite:** Provides high-level metrics on system performance and routing effectiveness.
-   **Extensible Architecture:** Easy to add new models or routing logic.
-   **Self-Improving:** Automatically learns from user feedback and manual overrides.
