import json
import os

# File to store scores
SCORES_FILE = "scores.json"

# Sample quiz data (can be expanded or replaced by API later)
quiz_data = [
    {"question": "What is the capital of India?", "answer": "New Delhi"},
    {"question": "Who wrote the Ramayana?", "answer": "Valmiki"},
    {"question": "What is 12 * 8?", "answer": "96"},
    {"question": "Which planet is known as the Red Planet?", "answer": "Mars"},
]

# Load scores if file exists
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {}

# Save scores
def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=4)

# Show leaderboard
def show_leaderboard(scores):
    print("\n🏆 Leaderboard (Top 5):")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (user, score) in enumerate(sorted_scores[:5], 1):
        print(f"{i}. {user} → {score} points")

def run_quiz(username):
    scores = load_scores()
    user_score = scores.get(username, 0)

    print(f"\nWelcome {username}! Your current score: {user_score}")
    print("Let's start the quiz! 🎯\n")

    for q in quiz_data:
        ans = input(q["question"] + " ")
        if ans.strip().lower() == q["answer"].lower():
            print("✅ Correct!")
            user_score += 1
        else:
            print(f"❌ Wrong! Correct answer is: {q['answer']}")

    scores[username] = user_score
    save_scores(scores)

    print(f"\n{username}, your total score is now: {user_score}")
    show_leaderboard(scores)

if __name__ == "__main__":
    name = input("Enter your name: ")
    run_quiz(name)
