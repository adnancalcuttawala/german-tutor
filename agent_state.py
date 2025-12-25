def call_llm(self, prompt):
    r = requests.post(
        self.api_url,
        headers=self.headers,
        json={"inputs": prompt},
        timeout=30
    )

    data = r.json()

    # Case 1: HF returns list
    if isinstance(data, list) and len(data) > 0:
        return data[0].get("generated_text", "⚠️ No text generated.")

    # Case 2: HF returns dict
    if isinstance(data, dict):
        if "generated_text" in data:
            return data["generated_text"]
        if "error" in data:
            return f"⚠️ Model error: {data['error']}"

    return "⚠️ LLM did not return a valid response."
