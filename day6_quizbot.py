# day6_quizbot.py
import random
import sys
from utils import is_gemini_available, safe_generate, mock_response, load_scores, save_scores

MODEL_NAME = "gemini-1.5-flash"

LOCAL_MCQS = [
    {"question": "What is the capital of France?", "options": ["A) Berlin", "B) London", "C) Paris", "D) Madrid"], "answer": "C"},
    {"question": "Which planet is largest?", "options": ["A) Earth", "B) Jupiter", "C) Mars", "D) Saturn"], "answer": "B"},
    {"question": "What is 5 + 7?", "options": ["A)10","B)11","C)12","D)13"], "answer": "C"},
]

def parse_resp_mcq(raw_text):
    # Very tolerant parser: find Question: ... Options: A) ... B) ... C) ... D) ... Answer: X
    import re
    m = re.search(r"Question:\s*(.+?)\nOptions:\s*(.+?)\nAnswer:\s*([A-D])", raw_text, re.DOTALL | re.IGNORECASE)
    if not m:
        return None
    q = m.group(1).strip()
    opts_block = m.group(2).strip()
    ans = m.group(3).strip().upper()
    opts = []
    for line in opts_block.splitlines():
        line = line.strip()
        if line and (line[0].upper() in "ABCD"):
            opts.append(line)
    if len(opts) < 4:
        # attempt splitting by A) B) C) D)
        parts = re.split(r"\n(?=[A-D]\))", opts_block)
        opts = [p.strip() for p in parts if p.strip()]
    if len(opts) >= 4:
        return {"question": q, "options": opts[:4], "answer": ans}
    return None

def generate_mcq(subject="General Knowledge", difficulty="Easy"):
    prompt = f"You are an exam setter. Generate exactly ONE {difficulty} level MCQ on the topic: {subject}.\nFormat:\nQuestion: <...>\nOptions:\nA) ...\nB) ...\nC) ...\nD) ...\nAnswer: <A/B/C/D>"
    if is_gemini_available():
        ok, txt = safe_generate(prompt)
        if ok:
            parsed = parse_resp_mcq(txt)
            if parsed:
                return parsed, txt
            else:
                return None, txt
        else:
            # gemini call failed — fallback to mock
            return None, txt
    else:
        return random.choice(LOCAL_MCQS), "(mock)"

def play_round():
    scores = load_scores()
    name = input("Name: ").strip() or "Player"
    subject = input("Subject (Math/Science/GK): ").strip() or "GK"
    difficulty = input("Difficulty (Easy/Medium/Hard): ").strip().capitalize() or "Easy"
    try:
        qcount = int(input("How many questions? (default 3): ").strip())
    except Exception:
        qcount = 3

    correct = 0
    for i in range(qcount):
        parsed, raw = generate_mcq(subject, difficulty)
        if parsed is None:
            # raw may contain fallback MCQ text; try to parse; otherwise pick local
            parsed = None
            try:
                parsed = parse_resp_mcq(raw)
            except Exception:
                parsed = None
        if parsed is None:
            parsed = random.choice(LOCAL_MCQS)
            raw = "(local fallback)"

        print(f"\nQ{i+1}: {parsed['question']}")
        for opt in parsed["options"]:
            print(opt)
        ans = input("Your answer (A/B/C/D): ").strip().upper()
        if ans == parsed["answer"]:
            print("Correct ✅")
            correct += 1
        else:
            print(f"Wrong ❌ — correct: {parsed['answer']}")
    # update scores
    user_scores = scores.get(name, {})
    user_scores[subject] = user_scores.get(subject, 0) + correct
    scores[name] = user_scores
    save_scores(scores)
    print(f"\n{name} scored {correct}/{qcount} — saved to scores.json")

def main():
    print("Day6 Quizbot — menu: 1) Play  2) Leaderboard  3) Exit")
    while True:
        choice = input("Choose: ").strip()
        if choice == "1":
            play_round()
        elif choice == "2":
            scores = load_scores()
            if not scores:
                print("No scores yet.")
            else:
                ranking = []
                for user, subj_map in scores.items():
                    total = sum(subj_map.values()) if isinstance(subj_map, dict) else subj_map
                    ranking.append((user, total))
                ranking.sort(key=lambda x: x[1], reverse=True)
                for i, (u, t) in enumerate(ranking[:10], start=1):
                    print(f"{i}. {u} — {t} pts")
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
