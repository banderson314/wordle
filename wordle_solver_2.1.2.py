# Made by Brandon Anderson

import random
import os
import time
import math


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
            feedback += "R"  # Red/not in the word
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


        count += 1
        percent_done = int(100*count/total_words_to_process)
        progress_message = f"Processed {count}/{total_words_to_process} words. {percent_done}%"
        print(progress_message, end="\r")

    blank_message = " " * len(progress_message)
    print(blank_message, end="\r")

    return best_words

def provide_best_words_regardless_of_feedback(remaining_words):
    options_given = 10      # Will provide the 10 best options, unless there are less than 10 total remaining
    answer_options_given = 10
    best_words = []   # We will be making two lists. One of top best words and another of top best words that follow feedback (potential answers)
    best_potential_answers = []

    if len(remaining_words) < options_given:
        answer_options_given = len(remaining_words)

    total_words_to_process = len(original_word_list)    # Initiating progress message
    count = 0
    print(f"Processed {count}/{total_words_to_process} words", end="\r")
    previous_percent_done = 0
    loop_start_time = time.time()
    prev_progress_message_length = 0

    for proposed_guess_word in original_word_list:   # By using original_word_list instead of remaining_words, we consider all words as potential guesses

        average_reduction = optimal_word_selection(proposed_guess_word, remaining_words)

        if proposed_guess_word in remaining_words:
            is_potential_answer = True
        else:
            is_potential_answer = False

        # Adding to list of best words
        if len(best_words) < options_given:
            best_words.append((proposed_guess_word, average_reduction, is_potential_answer))
            best_words.sort(key=lambda x: x[1], reverse=True)
        elif average_reduction > best_words[-1][1]:
            best_words.pop()
            best_words.append((proposed_guess_word, average_reduction, is_potential_answer))
            best_words.sort(key=lambda x: x[1], reverse=True)

        # Adding to list of best potential answers
        if proposed_guess_word in remaining_words:
            if len(best_potential_answers) < answer_options_given:
                best_potential_answers.append((proposed_guess_word, average_reduction))
                best_potential_answers.sort(key=lambda x: x[1], reverse=True)
            elif average_reduction > best_potential_answers[-1][1]:
                best_potential_answers.pop()
                best_potential_answers.append((proposed_guess_word, average_reduction))
                best_potential_answers.sort(key=lambda x: x[1], reverse=True)



        # Updating the progress message
        count += 1
        percent_done = int(100*count/total_words_to_process)

        if percent_done != previous_percent_done:
            previous_percent_done = percent_done
            loop_end_time = time.time()
            loop_duration_time = loop_end_time - loop_start_time
            remaining_percentage = 100 - percent_done
            time_remaining = int(loop_duration_time * remaining_percentage)

            try:
                if time_remaining > previous_time_remaining:
                    time_remaining = previous_time_remaining
                previous_time_remaining = time_remaining
            except NameError:
                previous_time_remaining = time_remaining

            loop_start_time = time.time()

        #if count > 2:
        #    blank_message = " " * len(progress_message)
        #    print(blank_message, end="\r")

        try:
            if time_remaining < 61:
                progress_message = f"Processed {count}/{total_words_to_process} words. Time remaining: {time_remaining} s. {percent_done}% done."
            else:
                minutes_remaining = math.floor(time_remaining / 60)
                seconds_remainder = time_remaining - (minutes_remaining * 60)
                progress_message = f"Processed {count}/{total_words_to_process} words. Time remaining: {minutes_remaining} min {seconds_remainder} s. {percent_done}% done."

        except NameError:
            progress_message = f"Processed {count}/{total_words_to_process} words. {percent_done}% done."

        progress_message_length = len(progress_message)
        if prev_progress_message_length > progress_message_length:
            blank_message = " " * prev_progress_message_length
            print(blank_message, end="\r")

        print(progress_message, end="\r")
        prev_progress_message_length = progress_message_length

    # Removing any words from best_potential_answers if they already appear in best_words
    best_potential_answers = [sublist for sublist in best_potential_answers if not any(sublist[0] == word[0] for word in best_words)]

    blank_message = " " * len(progress_message)
    print(blank_message, end="\r")

    return best_words, best_potential_answers


# Start of the wordle solver
print("\nWelcome to Wordle Solver\n")
total_possible_words = len(original_word_list)
print(f"Total words in dictionary: {total_possible_words}")


print("\nTwo methods are available.")
print("Enter '1' if you want the guesses to always follow the feedback given.")
print("Enter '2' if you want the guesses to also include words that have been rejected.")
mode = "play"
while True:
    method = input("Method: ").strip().upper()

    if method == "TEST":   # Enters test mode where the script picks a word and automatically provides feedback
        mode = "test"
        secret_word = random.choice(list(original_word_list)).upper()
        print(f"Secret word: {secret_word}")

    elif method in {"1", "2"}:
        break


remaining_words = original_word_list
attempts = 0


while attempts < 6:  # The code will stop after 6 tries
    if attempts == 0:   # The first word
        guess = input("\nGuess #1: ")
        guess = guess.upper()
        if guess == "OPTIONS":
            original_best_words_file = os.path.join(script_directory, "best_words.txt")
            with open(original_best_words_file, "r") as file:
                original_best_options = [line.strip() for line in file]
            for i, line in enumerate(original_best_options):
                if i > 2 and i < 13:
                    print(line)
            guess = input("\nGuess #1: ")
            guess = guess.upper()

    elif len(remaining_words) == 1: # If there is only one word left
        guess = remaining_words.pop()
        print(f"\nThe secret word is '{guess}'")
        print(f"Total attempts: {attempts + 1}")
        exit()

    else:
        if method == "1":
            best_words = provide_best_words_following_feedback(remaining_words)
        elif method == "2":
            best_words, best_potential_answers = provide_best_words_regardless_of_feedback(remaining_words)
        guess = best_words[0][0]

        # Giving the user the best words and then asking for the user to chose one
        if method == "1":
            #print("Best guesses to eliminate the most potential words:")
            for word in best_words:
                print(f"{word[0]}: {word[1]}")

        if method == "2":
            print("Best guesses to eliminate the most potential words:")
            for word in best_words:
                if word[2] is True:
                    print(f"{word[0]}: {word[1]}   <- potential answer")
                else:
                    print(f"{word[0]}: {word[1]}")

            print("Best guesses that follow the feedback:")
            for word in best_potential_answers:
                print(f"{word[0]}: {word[1]}")

        guess = input(f"\nGuess #{attempts + 1}: ")
        guess = guess.upper()

    if guess == "EXIT":
        exit()

    # The user then tells the computer what the feedback is from wordle, or they ask the computer for other word suggestions
    if mode == "play":
        feedback = provide_feedback()
    elif mode == "test":
        feedback = simulated_provide_feedback(secret_word, guess)
        print(f"Feedback: {feedback}")


    if feedback == "GGGGG" or feedback == "YES":
        print(f"\nThe secret word is '{guess}'")
        print(f"Total attempts: {attempts + 1}\n")
        exit()


    # Refine the list of remaining words based on feedback
    remaining_words = refine_possible_words(remaining_words, feedback, guess)
    attempts += 1

    print(f"Remaining possible words: {len(remaining_words)}")


    if len(remaining_words) == 0:
        print("Ran out of potential words\n")
        exit()

print("Ran out of guesses\n")
