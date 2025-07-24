from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import re
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
def extract_keywords(text):
    return [word.strip(".,!?") for word in text.split() if len(word) > 4]


# Tool B: Mock Web Search
def mock_web_search(keywords):
    return f"Search results for: {', '.join(keywords)}. Example content about {keywords[0]} and its importance."


# Tool C: Qwen Summarizer
def summarize_with_qwen(text):
    completion = client.chat.completions.create(
        model="qwen3:4b",
        messages=[
            {"role": "system", "content": "You are a helpful summarizer."},
            {"role": "user", "content": f"Summarize the following:\n\n{text}"}
        ]
    )
    return completion.choices[0].message.content


# Tool D: Calculator
def evaluate_math_expression(expression):
    try:
        # VERY simple safe eval for math only
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


# Tool Router: Detect if input is math
def is_math_expression(text):
    return bool(re.fullmatch(r"[\d\s\+\-\*\/\.\(\)]+", text.strip()))

# --- Parallel-safe versions of your tools ---
def safe_extract_keywords(user_input):
    try:
        return extract_keywords(user_input)
    except Exception:
        return []  # fallback

def safe_mock_search(keywords):
    try:
        return mock_web_search(keywords)
    except Exception:
        return "Search failed."

def safe_summarize(text):
    try:
        return summarize_with_qwen(text)
    except Exception:
        return "Summary generation failed."

def safe_calculate(expression):
    try:
        return evaluate_math_expression(expression)
    except Exception:
        return "Invalid math expression."


# --- Parallel Orchestrator ---
def multi_tool_assistant(user_input):
    print("User Input:", user_input)

    if is_math_expression(user_input):
        print("🧮 Detected math input. Routing to calculator...")
        result = safe_calculate(user_input)
        print("Calculator Result:\n", result)
        return

    results = {}

    with ThreadPoolExecutor() as executor:
        # Step 1: Extract Keywords
        future_keywords = executor.submit(safe_extract_keywords, user_input)

        # Wait for keywords first (used by next step)
        keywords = future_keywords.result()

        # Step 2 + 3: Run Search and Summary in parallel
        futures = {
            'search': executor.submit(safe_mock_search, keywords),
        }

        # Optional: Pre-summarize the user query as fallback (if needed)
        if keywords:
            search_result = futures['search'].result()
            futures['summary'] = executor.submit(safe_summarize, search_result)

        # Collect Results
        for name, future in futures.items():
            try:
                results[name] = future.result()
            except Exception as e:
                print(f"[{name.upper()} ERROR] {e}")
                results[name] = f"{name} failed."

    # Final Output
    if 'summary' in results:
        print("\nQwen Summary:\n", results['summary'])
    else:
        print("\nNo summary generated.")
    print("\nSearch Result:\n", results.get('search'))

if __name__ == "__main__":
    user_query = "25+25"
    multi_tool_assistant(user_query)