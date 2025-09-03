# day10_quiz_eval.py
from utils import is_gemini_available, safe_generate, mock_response, load_scores, save_scores

conversation = []

def ask_with_context(user_text):
    # join last few messages (safe small context)
    ctx = "\n".join(f"User: {m['u']}\nBot: {m['b']}" for m in conversation[-6:])
    prompt = f"Conversation so far:\n{ctx}\nUser: {user_text}\nAssistant:"
    if is_gemini_available():
        ok, txt = safe_generate(prompt)
        if ok:
            return txt
        return f"(error) {txt}"
    else:
        return mock_response(prompt)

def main():
    print("Day10 — multi-turn. type exit to quit")
    while True:
        u = input("You: ").strip()
        if u.lower() in ("exit","quit"):
            print("Bye")
            break
        a = ask_with_context(u)
        print("Bot:", a)
        conversation.append({"u": u, "b": a})

if __name__ == "__main__":
    main()
