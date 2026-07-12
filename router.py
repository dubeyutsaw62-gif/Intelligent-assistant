import os
import json
import sys
from openai import OpenAI

def load_tasks(input_path="/input/tasks.json"):
    if not os.path.exists(input_path):
        print(f"Error: Input file missing at {input_path}")
        sys.exit(1)
    with open(input_path, "r") as f:
        return json.load(f)

def save_results(results, output_path="/output/results.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

def analyze_and_optimize_task(prompt, allowed_models):
    cheap_model = allowed_models[0]
    expensive_model = allowed_models[-1]
    
    for model in allowed_models:
        model_lower = model.lower()
        if any(keyword in model_lower for keyword in ["8b", "mini", "flash", "lite"]):
            cheap_model = model
        elif any(keyword in model_lower for keyword in ["70b", "coder", "pro", "plus", "large"]):
            expensive_model = model
            
    if cheap_model == expensive_model and len(allowed_models) > 1:
        cheap_model = allowed_models[0]
        expensive_model = allowed_models[-1]

    cleaned_prompt = " ".join(prompt.split())
    lower_prompt = cleaned_prompt.lower()

    complex_keywords = [
        "def ", "function", "bug", "fix", "code", "python", 
        "matrix", "array", "solve", "how many items remain",
        "who owns", "logic", "puzzle", "refactor", "async"
    ]
    
    is_complex = any(keyword in lower_prompt for keyword in complex_keywords) or len(cleaned_prompt) > 500
    target_model = expensive_model if is_complex else cheap_model

    system_instruction = "You are a precise, cost-optimized utility agent. "
    
    if "one sentence" in lower_prompt:
        system_instruction += "You MUST restrict your entire response to exactly one single sentence. Do not add any conversational filler."
    elif "sentiment" in lower_prompt or "classify" in lower_prompt:
        system_instruction += "You are a strict classifier. Output ONLY the final classification label (e.g., Positive, Negative, Neutral) and absolutely nothing else."
    elif "extract" in lower_prompt:
        system_instruction += "Extract the requested data concisely. Do not explain your extraction process."
    elif is_complex:
        system_instruction += "Provide the exact code or logical answer. Do not include markdown formatting, pleasantries, or step-by-step explanations unless explicitly requested."
    else:
        system_instruction += "Respond directly to the user instruction with no extra conversational text."

    safe_max_tokens = 1024 

    return target_model, cleaned_prompt, safe_max_tokens, system_instruction

def main():
    # STRICT PRODUCTION MODE: Reading entirely from the harness environment
    try:
        api_key = os.environ["FIREWORKS_API_KEY"]
        base_url = os.environ["FIREWORKS_BASE_URL"]
        allowed_models = os.environ["ALLOWED_MODELS"].split(",")
    except KeyError as e:
        print(f"Fatal Error: Missing injected environment variable {e}")
        sys.exit(1)

    client = OpenAI(base_url=base_url, api_key=api_key)
    tasks = load_tasks()
    results = []

    print(f"Loaded {len(tasks)} tasks. Starting execution...")

    for item in tasks:
        task_id = item["task_id"]
        original_prompt = item["prompt"]

        target_model, optimized_prompt, max_tokens, system_instruction = analyze_and_optimize_task(original_prompt, allowed_models)

        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": optimized_prompt}
                ],
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            raw_content = response.choices[0].message.content
            if raw_content:
                answer = raw_content.strip()
            else:
                answer = "Error: Model returned an empty response."
                
        except Exception as api_error:
            print(f"API Failure on {task_id}: {api_error}")
            answer = "Error generating response down pipeline."

        results.append({
            "task_id": task_id,
            "answer": answer
        })

    save_results(results)
    print("Execution complete. Output saved successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()