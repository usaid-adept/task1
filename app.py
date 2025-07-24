import re
from openai import OpenAI

# Initialize Ollama Client
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


# Tool A: Keyword Extractor
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


# Main Orchestrator
def multi_tool_assistant(user_input):
    print("User Input:", user_input)

    if is_math_expression(user_input):
        print("🧮 Detected math input. Routing to Calculator.")
        result = evaluate_math_expression(user_input)
        print("Tool D - Calculator:\n", result)
        return

    keywords = extract_keywords(user_input)
    print("Tool A - Extracted Keywords:", keywords)

    search_results = mock_web_search(keywords)
    print("Tool B - Search Result:\n", search_results)

    summary = summarize_with_qwen(search_results)
    print("\nTool C - Qwen Summary:\n", summary)


# Run Demo
if __name__ == "__main__":
    examples = [
        "Tell me about the impact of solar power on rural communities.",
        "25*(3+7)"
    ]
    for query in examples:
        print("\n" + "="*50)
        multi_tool_assistant(query)
