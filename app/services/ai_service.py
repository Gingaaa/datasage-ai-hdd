import json
import requests
from app.core.config import settings

class AIService:
    @staticmethod
    def call_ollama(prompt: str, json_mode: bool = False) -> str:
        """Call the local Ollama instance for chat completion."""
        url = f"{settings.ollama_base_url}/generate"
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        
        if json_mode:
            payload["format"] = "json"
            
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling local Ollama: {e}")
            return ""

    @classmethod
    def generate_unified_report(cls, data_type: str, context: str) -> str:
        """Generates a comprehensive markdown report for the uploaded data."""
        if data_type in ['structured', 'tabular']:
            prompt = f"""
You are an expert Data Scientist and Senior Business Analyst. I have analyzed a tabular dataset and generated a statistical summary.
Based on the following JSON summary, please generate a highly detailed, expansive, and well-structured Analytics Report in Markdown format.

Your report must be exhaustive and include the following sections with deep elaboration:
1. **Executive Summary**: A thorough overview of the dataset's purpose, size, and potential business value.
2. **Comprehensive Data Dictionary**: For each column, infer its meaning, business context, data type, and its role within the dataset. Explain why this column is important.
3. **Deep-Dive Insights**: Break down the statistical metrics provided (null counts, unique counts, sample values) and explain what they signify for data quality and business operations. Are there anomalies? Are the categories evenly distributed?
4. **Strategic Recommendations**: Provide highly specific, actionable recommendations for further analysis, machine learning models, or business strategies based on the inferred data.

Dataset Summary:
{context}

Format the output strictly as Markdown. Do not include raw JSON. Write in a professional, analytical tone, and expand on your points significantly.
"""
        else:
            prompt = f"""
You are an expert Document Analyst. Please read the following extracted text from a document or media file and generate a comprehensive, well-structured Report in Markdown format.
Include:
1. Executive Summary
2. Key Topics / Themes
3. Detailed Breakdown of important points
4. Conclusion

Extracted Text (truncated if long):
{context[:4000]}  # Truncating to avoid context window issues

Format the output strictly as Markdown.
"""
        response_text = cls.call_ollama(prompt, json_mode=False)
        return response_text if response_text else "# Report Generation Failed\nCould not reach the AI service."

    @classmethod
    def chat_with_data(cls, user_message: str, context_str: str, is_rag: bool = False) -> str:
        """Interact with the dataset via natural language."""
        if is_rag:
            prompt = f"""
You are a helpful assistant. Use the following context to answer the user's question.
If the context does not contain the answer, say you don't know. Do not make up information.

Context:
{context_str}

Question: {user_message}
Answer:
"""
        else:
            prompt = f"""
You are an Intelligent Data Dictionary Agent. 
You are an assistant answering questions about a dataset.

You have access to the Statistical Summary (which contains sample values, unique counts, and null counts):
{context_str}

The user asks: "{user_message}"

Answer the user's question clearly and concisely based on the context provided.
IMPORTANT RULES:
1. You only have access to the sample values and statistical metadata above. You DO NOT have the full raw dataset.
2. If the user asks for "all unique product names" or similar, provide the sample values you have and explain that you can only see a small sample (and specify the total unique count based on the metadata). DO NOT output placeholders like "[list of unique product names]".
3. If the question is outside the scope of the dataset, politely inform them.
"""
        response_text = cls.call_ollama(prompt, json_mode=False)
        return response_text if response_text else "Error: Could not get a response from local Llama."

    @classmethod
    def chat_with_data_and_analytics(cls, user_message: str, summary_str: str, df) -> dict:
        """Interact with dataset, supporting automated proactive chart generation."""
        # Proactively detect if a chart is needed using a simple LLM query
        columns = list(df.columns) if df is not None else []
        intent_prompt = f"""
Analyze the following user request: "{user_message}"
Available tabular columns: {columns}

Does the user's request imply they want to see a distribution, comparison, count, or trend that would be best visualized as a chart (e.g., pie, bar, line)?
Even if they do not explicitly say "chart" or "graph", if the question asks "how many per category", "what is the distribution", "compare the sales", etc., a chart is appropriate.

If a chart is appropriate AND a relevant categorical/groupable column exists in the available columns list, return a JSON object:
{{
  "needs_chart": true,
  "type": "pie" or "bar",
  "column": "exact_column_name_from_list"
}}

If no chart is needed, or no suitable column exists, return:
{{
  "needs_chart": false
}}

Return ONLY the JSON object.
"""
        chart_data = None
        if df is not None and len(columns) > 0:
            intent_response = cls.call_ollama(intent_prompt, json_mode=True)
            try:
                if intent_response.strip().startswith("```json"):
                    intent_response = intent_response.strip()[7:-3]
                intent = json.loads(intent_response)
                
                if intent.get("needs_chart") and intent.get("column") in df.columns:
                    col = intent.get("column")
                    chart_type = intent.get("type", "bar")
                    
                    # Perform simple value counts analytics
                    counts = df[col].value_counts().head(10)
                    chart_data = {
                        "type": chart_type,
                        "labels": counts.index.astype(str).tolist(),
                        "values": counts.values.tolist(),
                        "title": f"Distribution of {col}"
                    }
            except Exception as e:
                print(f"Chart intent parsing failed: {e}")
                pass

        # Generate the normal text reply
        reply = cls.chat_with_data(user_message, summary_str, is_rag=False)
        
        if chart_data and "I've generated a chart" not in reply:
            reply += f"\n\n*I have also generated a {chart_data['type']} chart for `{chart_data['title']}` based on your request.*"
            
        return {"reply": reply, "chart_data": chart_data}

