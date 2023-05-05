from flask import Flask, render_template, request, redirect, session, flash
import random
import os
import threading
import pickle

app = Flask(__name__)
app.secret_key = os.urandom(24)

class Wordle:
    def __init__(self, file, max_tries):
        self.file = file
        self.words = []
        self.current_word = None
        self.max_tries = max_tries
        self.count = 0
        self.attempts = []
        self.true = True
        self.open_file()
        self.select_word()

    def open_file(self):
        with open(self.file, "r") as f:
            self.words = f.read().splitlines()

    def select_word(self):
        self.current_word = random.choice(self.words)

    def choose(self, input):
        if len(input) != 5:
            flash("not a 5 letter word", "warning")
            return None
        if input not in self.words:
            flash("not a word", "warning")
            return None
        self.count += 1
        split = list(input)
        if input == self.current_word:
            self.true = False
            flash("you won!", "win")
        if self.count > self.max_tries:
            self.true = False
            flash("Too many guesses game over", "warning")
        found = {}
        [found.update({x: [y, 1]}) if self.current_word[x] == y else found.update({x: [y, 0]}) for x, y in enumerate(split) if y in self.current_word]
        if found:
            self.get_formatted_attempt(input, found)
            return found
        else:
            found = {x: [y, 0] for x, y in enumerate(split)}
            self.get_formatted_attempt(input, found)
            return found

    def get_formatted_attempt(self, attempt, result):
        formatted = []
        for i, letter in enumerate(attempt):
            if i in result and result[i][1] == 1:
                formatted.append((letter, 'bg-green-500'))
            elif letter in self.current_word and (i not in result or result[i][1] == 0):
                formatted.append((letter, 'bg-orange-500'))
            else:
                formatted.append((letter, ''))
        self.attempts.append(formatted)
        return formatted
        
    def to_dict(self):
        return {
            "current_word": self.current_word,
            "max_tries": self.max_tries,
            "count": self.count,
            "attempts": self.attempts,
            "true": self.true
        }
        
    @classmethod
    def from_dict(cls, data, file):
        wordle = cls(file, data["max_tries"])
        wordle.current_word = data["current_word"]
        print(wordle.current_word)
        wordle.count = data["count"]
        wordle.attempts = data["attempts"]
        wordle.true = data["true"]
        return wordle

words_data = {}

@app.route('/')
def index():
    wordle = get_wordle()
    return render_template("index.html", attempts=wordle.attempts)

@app.route('/play', methods=['POST'])
def play():
    wordle = get_wordle()
    letters = [request.form.get(f'letter{i}') for i in range(5)]
    word = ''.join(letters)
    wordle.choose(word)
    session['wordle'] = wordle.to_dict()  # Update the session with the new state
    if not wordle.true:
        session["game_over"] = True
        wordle.attempts=[]
    return redirect("/")

@app.route('/play', methods=['GET'])
def plays():
    return redirect("/")

@app.route('/words_data')
def words_datas():
    return render_template('words_data.html', data=words_data)

def get_wordle():
    if 'wordle' not in session:
        wordle = Wordle("words.txt", 5)
        session['wordle'] = wordle.to_dict()
    else:
        wordle = Wordle.from_dict(session['wordle'], "words.txt")
        if wordle.true == False:
            wordle = Wordle("words.txt", 5)
            session['wordle'] = wordle.to_dict()
    return wordle

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="81")