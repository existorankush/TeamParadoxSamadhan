# day5_tutorbot.py
from utils import is_gemini_available, safe_generate, mock_response

INSTRUCTION_PREFIX = "You are a helpful tutor. Answer step by step with examples when possible.\nQuestion: "

def run_tutor():
    print("EduMentor Tutor — type 'exit' to quit.")
    while True:
        q = input("Student: ").strip()
        if q.lower() in ("exit", "quit"):
            print("Tutor: Goodbye!")
            break
        prompt = INSTRUCTION_PREFIX + q
        if is_gemini_available():
            ok, txt = safe_generate(prompt)
            if ok:
                print("Tutor:", txt)
            else:
                print("Tutor (error):", txt)
                print("Tutor (mock):", mock_response(prompt))
        else:
            print("Tutor (mock):", mock_response(prompt))

if __name__ == "__main__":
    run_tutor()
