import random

# Function to read words and hints from a file
def read_words_from_file(file_name):
    words_and_hints = []
    with open(file_name, "r") as file:
        for line in file:
            parts = line.strip().split(", ")
            if len(parts) == 2:
                words_and_hints.append((parts[0], parts[1]))
            else:
                print(f"Skipping invalid line: {line.strip()}")
    return words_and_hints

def initialize_game_state(file_name="words.txt", max_attempts=5):
    words_and_hints = read_words_from_file(file_name)
    word, hint = random.choice(words_and_hints)
    return {
        'word': word,
        'hint': hint,
        'attempts_left': max_attempts,
        'player_guesses': [],
        'revealed_word': "_ " * len(word),
        'hint_shown': False
    }

def process_guess(game_state, guess):
    word = game_state['word']
    player_guesses = game_state['player_guesses']
    attempts_left = game_state['attempts_left']
    hint_shown = game_state['hint_shown']

    player_guesses.append(guess)
    feedback = ""

    if guess in word:
        feedback = "Correct guess!"
    else:
        feedback = "Wrong guess!"
        attempts_left -= 1
        if not hint_shown:
            feedback += f"\nHint: {game_state['hint']}"
            hint_shown = True

    revealed_word = "".join([letter if letter in player_guesses else "_" for letter in word])

    game_state.update({
        'feedback': feedback,
        'revealed_word': " ".join(revealed_word),
        'attempts_left': attempts_left,
        'hint_shown': hint_shown
    })

    return game_state

def is_game_won(game_state):
    return all(letter in game_state['player_guesses'] for letter in game_state['word'])

def is_game_over(game_state):
    return game_state['attempts_left'] <= 0
