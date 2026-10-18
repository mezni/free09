import time
import json
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# ------------------------------------------------------------------
# Execution Trace Schema
# ------------------------------------------------------------------
@dataclass
class TraceStep:
    trace_id: str
    timestamp: float
    system_prompt: str
    user_prompt: str
    use_history: bool
    history_snapshot: List[Dict[str, str]]
    full_prompt_payload: List[Dict[str, str]]
    llm_response: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

TRACE_LOGS: Dict[str, TraceStep] = {}

# ------------------------------------------------------------------
# Chatbot Engine Logic
# ------------------------------------------------------------------
class ChatbotEngine:
    def __init__(self, system_prompt: str = "You are an AI developer assistant specializing in LLM observability and system architectures."):
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = []

    def set_system_prompt(self, new_prompt: str):
        self.system_prompt = new_prompt

    def clear_history(self):
        self.history = []

    def call_llm(self, payload: List[Dict[str, str]]) -> str:
        """
        Simulated LLM call. Swap with actual OpenAI / Gemini API call if desired:
        e.g., openai.chat.completions.create(model="gpt-4o", messages=payload)
        """
        time.sleep(0.38)  # Simulate network latency
        last_msg = payload[-1]["content"]
        return f"Echo response: '{last_msg}' [Processed with prompt: '{self.system_prompt[:35]}...']"

    def process_turn(self, user_input: str, use_history: bool = True) -> TraceStep:
        start_time = time.time()
        trace_id = f"trc-{uuid.uuid4().hex[:8]}"

        # Assemble prompt payload
        payload = [{"role": "system", "content": self.system_prompt}]
        history_snapshot = list(self.history) if use_history else []

        if use_history:
            payload.extend(self.history)
        
        payload.append({"role": "user", "content": user_input})

        # LLM Call
        response_text = self.call_llm(payload)
        end_time = time.time()

        # Update engine history
        if use_history:
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": response_text})

        # Calculate metrics & trace
        latency_ms = round((end_time - start_time) * 1000, 2)
        total_chars = sum(len(m["content"]) for m in payload) + len(response_text)
        prompt_tokens = max(10, total_chars // 4)
        completion_tokens = max(5, len(response_text) // 4)

        trace = TraceStep(
            trace_id=trace_id,
            timestamp=start_time,
            system_prompt=self.system_prompt,
            user_prompt=user_input,
            use_history=use_history,
            history_snapshot=history_snapshot,
            full_prompt_payload=payload,
            llm_response=response_text,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )

        TRACE_LOGS[trace_id] = trace
        return trace

# ------------------------------------------------------------------
# FastAPI Interface for Streamlit App
# ------------------------------------------------------------------
app = FastAPI(title="CLI Engine API")
bot = ChatbotEngine()

class ChatRequest(BaseModel):
    user_prompt: str
    system_prompt: Optional[str] = None
    use_history: bool = True

@app.post("/chat")
def chat(req: ChatRequest):
    if req.system_prompt is not None:
        bot.set_system_prompt(req.system_prompt)
    trace = bot.process_turn(req.user_prompt, use_history=req.use_history)
    return asdict(trace)

@app.get("/traces")
def get_traces():
    return [asdict(t) for t in TRACE_LOGS.values()]

@app.get("/history")
def get_history():
    return bot.history

@app.post("/reset")
def reset():
    bot.clear_history()
    return {"status": "success"}

# ------------------------------------------------------------------
# Interactive CLI Terminal Mode
# ------------------------------------------------------------------
def run_cli():
    print("==================================================")
    print(" 🛠️  CLI CHATBOT ENGINE (STANDALONE TERMINAL RUN)")
    print(" Commands: '/sys <prompt>', '/traces', 'exit'")
    print("==================================================\n")
    
    while True:
        try:
            user_in = input("User > ")
            if user_in.strip().lower() in ["exit", "quit"]:
                break
            elif user_in.startswith("/sys "):
                bot.set_system_prompt(user_in[5:].strip())
                print(f"System prompt updated to: '{bot.system_prompt}'\n")
                continue
            elif user_in.strip() == "/traces":
                print(json.dumps([asdict(t) for t in TRACE_LOGS.values()], indent=2))
                continue

            trace = bot.process_turn(user_in, use_history=True)
            print(f"Bot > {trace.llm_response}")
            print(f"  └─ Trace ID: {trace.trace_id} | Latency: {trace.latency_ms}ms | Tokens: {trace.total_tokens}\n")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        run_cli()
