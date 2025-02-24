from flask import Flask, render_template, request, redirect, url_for, session
import random
from hangman_words import word_list
from hangman_art import stages, logo

app = Flask(__name__)
app.secret_key = "your_secret_key_here" 

def init_game():
    session['lives'] = 6
    session['chosen_word'] = random.choice(word_list)
    session['correct_letters'] = []
    session['guessed_letters'] = []
    session['game_over'] = False
    session['message'] = "Welcome to Hangman! Make your first guess."

def get_display():
    chosen_word = session['chosen_word']
    correct_letters = session.get('correct_letters', [])
    display = ""
    for letter in chosen_word:
        if letter in correct_letters:
            display += letter
        else:
            display += "_"
    return display

@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize game if not already set
    if 'chosen_word' not in session:
        init_game()

    if request.method == "POST" and not session.get('game_over', False):
        guess = request.form.get("guess", "").lower().strip()
        if guess:
            guessed_letters = session['guessed_letters']
            if guess in guessed_letters:
                session['message'] = f"You've already guessed '{guess}'. Try a different letter."
            else:
                guessed_letters.append(guess)
                session['guessed_letters'] = guessed_letters

                if guess in session['chosen_word']:
                    correct_letters = session['correct_letters']
                    if guess not in correct_letters:
                        correct_letters.append(guess)
                    session['correct_letters'] = correct_letters
                    session['message'] = f"Good guess! '{guess}' is in the word."
                else:
                    session['lives'] -= 1
                    session['message'] = f"Oops! '{guess}' is not in the word."
                    if session['lives'] == 0:
                        session['game_over'] = True
                        session['message'] = f"You lose! The word was '{session['chosen_word']}'."

            # Check win condition
            if "_" not in get_display():
                session['game_over'] = True
                session['message'] = "Congratulations! You've guessed the word!"

        return redirect(url_for("index"))

    display_word = get_display()
    lives = session['lives']
    guessed_letters = session['guessed_letters']
    message = session['message']
    game_over = session['game_over']
    current_stage = stages[lives] if lives < len(stages) else ""
    return render_template("hangman.html",
                           logo=logo,
                           display_word=display_word,
                           lives=lives,
                           guessed_letters=guessed_letters,
                           message=message,
                           current_stage=current_stage,
                           game_over=game_over)

@app.route("/reset")
def reset():
    init_game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
