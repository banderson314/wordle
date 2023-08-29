# Made by Brandon Anderson

import random
import time

# Load the list of five-letter words
with open("D:/Scripts/Wordle/dictionary/five_letter_words_scholtes.txt", "r") as file:
    word_list = [line.strip() for line in file]
#with open("D:/Scripts/Wordle/dictionary/five_letter_words_short_list.txt", "r") as file:
#    word_list = [line.strip() for line in file]

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



def provide_multiple_options(remaining_words):
    options_given = 30      # Will provide the 30 best options, unless there are less than 30 total remaining
    if len(remaining_words) < options_given:
        options_given = len(remaining_words)
    best_words = []
    
    count = 0
    overall_start_time = time.time()

    for proposed_guess_word in remaining_words:
        word_start_time = time.time()
        if count > 0:
            previous_best = best_words[0][0]
        else:
            previous_best = ""
        count += 1
        
        average_reduction = optimal_word_selection(proposed_guess_word, remaining_words)
        
        word_end_time = time.time()
        elapsed_time = int(word_end_time - word_start_time)
        overall_elapsed_time = int((word_end_time - overall_start_time)/60) # Reported in minutes
        print(f"Word {count}/{len(remaining_words)}. {proposed_guess_word}: {average_reduction}. Time taken for the word: {elapsed_time} s. Total time taken: {overall_elapsed_time} min.")

        if len(best_words) < options_given:
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)
        elif average_reduction > best_words[-1][1]:
            best_words.pop()
            best_words.append((proposed_guess_word, average_reduction))
            best_words.sort(key=lambda x: x[1], reverse=True)

        if best_words[0][0] != previous_best:
            print(f"New best word! {best_words[0][0]}: {best_words[0][1]}")

    return best_words


total_possible_words = len(word_list)
print(f"Total words in dictionary: {total_possible_words}")

# Simulated Wordle game
remaining_words = set(word_list)
attempts = 0


best_words = provide_multiple_options(remaining_words)

for word in best_words:
    print(f"{word[0]}: {word[1]}")  # reporting the word followed by the average reduction

