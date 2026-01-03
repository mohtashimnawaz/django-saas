def sample_llm_response(n=5):
    return {
        "questions": [
            {"text": f"Sample Q{i}", "choices": ["A", "B", "C", "D"], "correct_index": 1} for i in range(1, n + 1)
        ]
    }
