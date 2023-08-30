# Made by Brandon Anderson

import random
import os

# Load the list of five-letter words
script_directory = os.path.dirname(os.path.abspath(__file__))
word_list_file = os.path.join(script_directory, "dictionary/five_letter_words_scholtes.txt")
with open(word_list_file, "r") as file:
    word_list = [line.strip() for line in file]

original_word_list = set(word_list)

# Function to compare two words and provide feedback
def provide_feedback():
    feedback = input("Enter feedback (G = Green, Y = Yellow, R = Red): ")
    feedback = feedback.upper()
    return feedback

def simulated_provide_feedback(secret_word, guess):
    feedback = ""
    for s, g in zip(secret_word, guess):
        if s == g:
            feedback += "G"  # Green
        elif g in secret_word:
            feedback += "Y"  # Yellow
        else:
            feedback += "R"  # Red
    return feedback


# Function to refine the list of possible words based on feedback
def refine_possible_words(possible_words, feedback, guess):
    refined_words = set()

    '''# If the guess contains multiple of the same letter(s), this logic is run
    def find_repeated_letters(guess):
        letters_in_word = {}
        repeated_letters = {}
        
        for i, letter in enumerate(guess):
            if letter in letters_in_word:
                repeated_letters.setdefault(letter, []).extend(
                    position for position in (letters_in_word[letter], i) if position not in repeated_letters[letter]
                )
            letters_in_word[letter] = i
        
        return repeated_letters
    
    repeated_letters_in_guess = find_repeated_letters(guess)
    if repeated_letters_in_guess:   # if there are repeated letters do this
        
        for letter in repeated_letters_in_guess:    # needed if there are multiple repeated letters
            
            feedback_on_repeated_letters = []
            positions_of_letter = repeated_letters_in_guess[letter] # get all the positions of the repeated letter
            for i in positions_of_letter:
                feedback_on_repeated_letters.append(feedback[i])    # give the feedback for each of the repeated letters
            
            g_and_y_count = 0
            r_count = 0
            for fb in feedback_on_repeated_letters:
                if fb == "G" or fb == "Y":
                    g_and_y_count += 1
                elif fb == "R":
                    r_count += 1
            
            def refine_words_with_repeats(possible_words, letter, count):
                new_possible_words = set()
                for word in possible_words:
                    if word.count(letter) == count:
                        new_possible_words.add(word)
                return new_possible_words
            
            new_possible_words = refine_words_with_repeats(possible_words, letter, g_and_y_count)
            possible_words = new_possible_words
            
            if r_count > 0:    # Changing the feedback to something the the next code can handle (changing R's to Y's if that letter actually exists somewhere)
                for i, fb in enumerate(feedback):
                    if i in positions_of_letter and fb == "R":
                        feedback = feedback[:i] + "Y" + feedback[i + 1:]'''
    

    # Eliminating potential words quickly based off of the presence (not position) of the letters
    g_and_y_letters = set()
    r_letters = set()
    for i, letter in enumerate(guess):
        if feedback[i] == "G" or feedback[i] == "Y":
            g_and_y_letters.add(letter)
        elif feedback[i] == "R":
            r_letters.add(letter)
    
    new_possible_words = set()
    for word in possible_words:
        if all(letter in word for letter in g_and_y_letters) and not any(letter in word for letter in r_letters):
            new_possible_words.add(word)
    possible_words = new_possible_words


    # Now looping through all possible words and matching the letter feedback
    for word in possible_words:
        valid_word = True

        for i, (fb, pw) in enumerate(zip(feedback, word)):
            if fb == "G" and pw != guess[i]:
                valid_word = False
                break
            if fb == "Y" and pw == guess[i]:
                valid_word = False
                break
        
        if valid_word == False:
            continue

        for i, (fb, gw) in enumerate(zip(feedback, guess)):
            if fb == "R" and gw in word:
                valid_word = False
                break
            if fb == "Y" and gw not in word:
                valid_word = False
                break

        if valid_word:
            refined_words.add(word)

    return refined_words



def optimal_word_selection(proposed_guess_word, remaining_words):

    all_possible_reductions = []

    for potential_solution in remaining_words:
        potential_feedback = simulated_provide_feedback(potential_solution, proposed_guess_word)
        potential_remaining_words = refine_possible_words(remaining_words, potential_feedback, proposed_guess_word)

        potential_reduction = len(remaining_words) - len(potential_remaining_words)
        all_possible_reductions.append(potential_reduction)

    average_reduction = sum(all_possible_reductions) / len(all_possible_reductions)

    return average_reduction



def provide_best_words_following_feedback(remaining_words):
    options_given = 10      # Will provide the 10 best options, unless there are less than 10 total remaining
    if len(remaining_words) < options_given:
        options_given = len(remaining_words)
    best_words = []

    if method == "1":   # Only need the feedback if user selected 1. provide_best_words_regardless_of_feedback does sometimes call this function and this isn't needed
        total_words_to_process = len(remaining_words)
        count = 0
        print(f"Processed {count}/{total_words_to_process} words", end="\r")

    for proposed_guess_word in remaining_words:

        average_reduction = optimal_word_selection(proposed_guess_word, remaining_words)

        if len(best_words) < options_given:
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)
        elif average_reduction > best_words[-1][1]:
            best_words.pop()
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)

        if method == "1":
            count += 1
            percent_done = int(100*count/total_words_to_process)
            progress_message = f"Processed {count}/{total_words_to_process} words. {percent_done}%"
            print(progress_message, end="\r")
    
    if method == "1":
        print("\n")

    return best_words

def provide_best_words_regardless_of_feedback(remaining_words):
    options_given = 10      # Will provide the 10 best options, unless there are less than 10 total remaining
    best_words = []
    

    total_words_to_process = len(original_word_list)
    count = 0
    print(f"Processed {count}/{total_words_to_process} words", end="\r")

    for proposed_guess_word in original_word_list:   # By using original_word_list instead of remaining_words, we consider all words as potential guesses
        
        average_reduction = optimal_word_selection(proposed_guess_word, remaining_words)

        if len(best_words) < options_given:
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)
        elif average_reduction > best_words[-1][1]:
            best_words.pop()
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)

        count += 1
        percent_done = int(100*count/total_words_to_process)
        progress_message = f"Processed {count}/{total_words_to_process} words. {percent_done}%"
        print(progress_message, end="\r")
    
    print("\n")

    # If all of the reduction scores are the same, that usually means there are only a couple answers left, so we will just report the words that follow the feedback given
    reduction_scores = [guess_and_score[1] for guess_and_score in best_words]
    if all(score == reduction_scores[0] for score in reduction_scores):
        best_words = provide_best_words_following_feedback(remaining_words)


    return best_words


# Start of the wordle solver
print("\nWelcome to Wordle Solver\n")
total_possible_words = len(original_word_list)
print(f"Total words in dictionary: {total_possible_words}")

print("Two methods are available.")
print("Enter '1' if you want the guesses to always follow the feedback given.")
print("Enter '2' if you want the guesses to also include words that have been rejected.\n")
method = input("Method: ")
while method != "1" and method != "2":
    print("Invalid input. Please enter 1 or 2.")
    method = input("Method: ")


remaining_words = original_word_list
attempts = 0


while attempts < 6:  # The code will stop after 6 tries
    if attempts == 0:
        guess = input("First guess: ")
        guess = guess.upper()
        if guess == "OPTIONS":
            original_best_words_file = os.path.join(script_directory, "best_words.txt")
            with open(original_best_words_file, "r") as file:
                original_best_options = [line.strip() for line in file]
            for i, line in enumerate(original_best_options):
                if i > 2 and i < 13:
                    print(line)
            guess = input("First guess: ")
            guess = guess.upper()
    elif len(remaining_words) == 1:
        guess = remaining_words.pop()
        print(f"The secret word is '{guess}'")
        print(f"Total attempts: {attempts + 1}")
        exit()
    else:
        if method == "1":
            best_words = provide_best_words_following_feedback(remaining_words)
        elif method == "2":
            best_words = provide_best_words_regardless_of_feedback(remaining_words)
        guess = best_words[0][0]

    print(f"Attempt {attempts + 1}: Guessing '{guess}'")

    feedback = provide_feedback()

    if feedback == "OPTIONS":
        for word in best_words:
            print(f"{word[0]}: {word[1]}")  # reporting the word followed by the average reduction
        guess = input("Next guess: ")
        guess = guess.upper()
        feedback = provide_feedback()

    if feedback == "GGGGG" or feedback == "YES":
        print(f"The secret word is '{guess}'")
        print(f"Total attempts: {attempts + 1}")
        exit()

    # Refine the list of remaining words based on feedback
    remaining_words = refine_possible_words(remaining_words, feedback, guess)
    attempts += 1

    print(f"Remaining possible words: {len(remaining_words)}")


    if len(remaining_words) == 0:
        print("Ran out of potential words")
        exit()

print("Ran out of guesses")
