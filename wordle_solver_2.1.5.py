# Made by Brandon Anderson

import random
import os
import time
import math
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import platform
import re
import ast


# Load the list of five-letter words
script_directory = os.path.dirname(os.path.abspath(__file__))
word_list_file = os.path.join(script_directory, "dictionary/five_letter_words_scholtes.txt")
with open(word_list_file, "r") as file:
    word_list = [line.strip() for line in file]
original_word_list = set(word_list)


# Reading the presolved document, or creating it if it doesn't exist
presolved_document = os.path.join(script_directory, "dictionary/presolved_words.txt")
if not os.path.exists(presolved_document):
    with open(presolved_document, "w"):
        pass
with open(presolved_document, "r") as file:
    presolved_words_string = [line.strip() for line in file]
# Converting the document into something python can read as lists    
presolved_words = []
for line in presolved_words_string:
    presolved_words.append(ast.literal_eval(line))



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

    #############
    '''
    original_feedback = feedback
    original_possible_words_len = len(possible_words)
    #print(f"1. Guess: {guess}. Feedback: {feedback}. Possible words: {len(possible_words)}")
    
    # Checks to see if there are repeated letters in the guess
    def find_repeated_letters(guess):
        #print(f"Here is the guess: {guess}")
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

            #if r_count > 0:    # Changing the feedback to something the the next code can handle (changing R's to Y's if that letter actually exists somewhere)
            #    for i, fb in enumerate(feedback):
            #        if i in positions_of_letter and fb == "R":
            #            feedback = feedback[:i] + "Y" + feedback[i + 1:]
    '''
    ########
    

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


    # Now looping through all possible words and matching the letter feedback based on position
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

    # Initiating progress message
    if mode != "presolve":
        total_words_to_process = len(original_word_list)    
        count = 0
        print(f"Processed {count}/{total_words_to_process} words", end="\r")
        previous_percent_done = 0
        loop_start_time = time.time()
        prev_progress_message_length = 0

    # By using original_word_list instead of remaining_words, we consider all words as potential guesses
    for proposed_guess_word in original_word_list:   

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
        if mode != "presolve":
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

    if mode != "presolve":
        blank_message = " " * len(progress_message)
        print(blank_message, end="\r")

    return best_words, best_potential_answers


def locate_wordle_on_screen():
    # Capture the screen and convert to a NumPy array
    screenshot = pyautogui.screenshot()
    screen_img = np.array(screenshot)

    # Ensure that the image has only three channels (RGB) and remove alpha channel
    if screen_img.shape[2] == 4:
        screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2RGB)

    # Convert to grayscale
    grey_img = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(grey_img, threshold1=30, threshold2=100)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on aspect ratio (1:1)
    aspect_ratio_tolerance = 0.01  # You can adjust this tolerance as needed
    filtered_contours = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h

        # Check if the aspect ratio is close to 1:1 within the tolerance
        if 1 - aspect_ratio_tolerance <= aspect_ratio <= 1 + aspect_ratio_tolerance:
            filtered_contours.append(contour)

    # Filtering contours based on size
    contours_to_keep = []
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area > 1500:
            contours_to_keep.append(contour)
    filtered_contours = contours_to_keep

    # Draw contours and rectangles on the original image for visualization
    image_with_contours = screen_img.copy()
    cv2.drawContours(image_with_contours, filtered_contours, -1, (0, 255, 0), 2)  # Green contours
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image_with_contours, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red rectangles

    # Calculate the coordinates of the grid
    grid_coordinates = []
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        grid_coordinates.append((x, y, x + w, y + h))
        #grid_coordinates.append((x, y, w, h))
    grid_coordinates = sorted(grid_coordinates, key=lambda x: (x[0], x[1]))


    def is_contained(coord1, coord2):
        # Check if coord1 is completely contained within coord2.
        # coord1 and coord2 are tuples of (x1, y1, x2, y2).
        x1_1, y1_1, x2_1, y2_1 = coord1
        x1_2, y1_2, x2_2, y2_2 = coord2

        return x1_1 >= x1_2 and y1_1 >= y1_2 and x2_1 <= x2_2 and y2_1 <= y2_2

    def remove_contained_coordinates(coordinates):
        # Remove coordinates that are completely contained within others.
        filtered_coordinates = []
        for i, coord1 in enumerate(coordinates):
            is_contained_by_other = False
            for j, coord2 in enumerate(coordinates):
                if i != j and is_contained(coord1, coord2):
                    is_contained_by_other = True
                    break
            if not is_contained_by_other:
                filtered_coordinates.append(coord1)
        return filtered_coordinates

    grid_coordinates = remove_contained_coordinates(grid_coordinates)

    if len(grid_coordinates) != 30:
        print("Error in locating the wordle grid. Should only detect 30 boxes on screen but that is not the case.")
        print(f"Number of boxes: {len(grid_coordinates)}")
        cv2.imshow(f"Number of boxes seen: {len(grid_coordinates)}", image_with_contours)
        cv2.waitKey(10_000)
        cv2.destroyAllWindows()
        exit()

    # Creating y coordinates for each row
    unique_y1_values = set()
    row_coordinates = []
    unique_x1_values = set()
    column_coordinates = []

    for coord in grid_coordinates:
        x1, y1, _, _ = coord  # Extract the x1 value from the coordinate
        if y1 not in unique_y1_values:
            unique_y1_values.add(y1)
            row_coordinates.append(y1+5)
        if x1 not in unique_x1_values:
            unique_x1_values.add(x1)
            column_coordinates.append(x1+5)

    return row_coordinates, column_coordinates












def get_feedback_automatically(attempt_number):
    # Get the RGB color at each coordinate in the first row
    colors = []
    current_row = row_coordinates[attempt_number]
    for column in column_coordinates:
        pixel_color = pyautogui.pixel(column, current_row)
        colors.append(pixel_color)

    def rgb_to_color_name(rgb):
        # First looking to see if it is black/white/grey
        range_of_rgb = max(rgb) - min(rgb)
        if range_of_rgb < 11:
            if min(rgb) > 180:
                return "white"
            else:
                return "black"

        standard_colors = {
            "yellow": (255, 255, 0),
            "green": (0, 128, 0),
        }

        # Find the closest matching  color
        min_distance = float('inf')
        closest_color = None

        for color, standard_rgb in standard_colors.items():
            r1, g1, b1 = rgb
            r2, g2, b2 = standard_rgb
            distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_color = color

        return closest_color

    colors = [rgb_to_color_name(rgb) for rgb in colors]
    color_to_char = {
        "yellow": "Y",
        "black": "R",
        "green": "G"
    }
    # Map the colors to characters and join them into a string
    feedback = "".join(color_to_char.get(color, "") for color in colors)
    return feedback

def input_word_into_wordle(guess):
    x, y = pyautogui.position()
    pyautogui.click(column_coordinates[0], row_coordinates[0])
    pyautogui.moveTo(x, y)
    pyautogui.typewrite(guess)
    pyautogui.press('enter')
    time.sleep(1.5)
    if platform.system() == 'Windows':
        pyautogui.hotkey('alt', 'tab')
    elif platform.system() == 'Darwin':  # macOS
        pyautogui.hotkey('command', 'tab')
    else:
        pass




##############################################
######### Start of the wordle solver #########
##############################################

print("\nWelcome to Wordle Solver\n")
total_possible_words = len(original_word_list)
print(f"Total words in dictionary: {total_possible_words}")


print("\nTwo methods are available.")
print("Enter '1' if you want the guesses to always follow the feedback given.")
print("Enter '2' if you want the guesses to also include words that have been rejected.")
mode = "play"
while True:
    method = input("Method: ").strip().upper()
    user_given_answer = re.match(r"TEST (\w{5})", method)
    presolve_word = re.match(r"PRESOLVE (\w{5})", method)

    # Enters test mode where the script picks a word and automatically provides feedback
    if method == "TEST":
        mode = "test"
        secret_word = random.choice(list(original_word_list)).upper()
        print(f"Secret word: {secret_word}")
    
    # If the user wants to run test mode using a specific word as the answer
    elif user_given_answer:
        mode = "test"
        secret_word = user_given_answer.group(1)
        print(f"Secret word: {secret_word}")

    elif presolve_word:
        word_to_presolve = presolve_word.group(1)
        mode = "presolve"
        break

    elif method == "AUTO":
        row_coordinates, column_coordinates = locate_wordle_on_screen()
        mode = "auto"
        print("Wordle grid is located. Please do not cover it up or move it while playing.")

        #print(f"Row coordinates: {row_coordinates}")
        #print(f"Column coordinates: {column_coordinates}")

    elif method in {"1", "2"}:
        break




# [word, {feedback: [best_words, best_potential_words]}]
# If the user specified presolve mode
if mode == "presolve":
    # Checking if the word has already been presolved
    for word in presolved_words:
        if word[0] == word_to_presolve:
            print(f"{word_to_presolve} has already been presolved.")
            print(f"If this is in error, go to the presolved document and delete the entry for {word_to_presolve}")
            exit()
    
    print(f"Presolving for: {word_to_presolve}")
    
    potential_feedbacks = set()
    for word in original_word_list:
        feedback = simulated_provide_feedback(word, word_to_presolve)
        if feedback not in potential_feedbacks:
            potential_feedbacks.add(feedback)
    
    feedback_and_answers_dict = {}
    for i, feedback in enumerate(potential_feedbacks):
        remaining_words = refine_possible_words(original_word_list, feedback, word_to_presolve)
        print(f"\n{feedback}: {len(remaining_words)}")

        best_words, best_potential_answers = provide_best_words_regardless_of_feedback(remaining_words)    
        if len(remaining_words) <= 2:
            best_words = []


        feedback_and_answers_dict[feedback] = [best_words, best_potential_answers]

        print(f"Best words: {best_words}")
        print(f"Best potential answers: {best_potential_answers}")
        print(f"Remaining feedbacks to simulate: {len(potential_feedbacks)-i-1}")


    # Saving the answers found in presolved_words.txt
    presolve_document_entry = [word_to_presolve, feedback_and_answers_dict]
    presolve_document_entry = str(presolve_document_entry) + "\n"
    with open(presolved_document, "a") as file:
        file.write(presolve_document_entry)
    
    exit()




# If not in presolve mode, running the code normally:
remaining_words = original_word_list
attempts = 0
while attempts < 6:  # The code will stop after 6 tries
    if attempts == 0:   # The first word
        guess = input("\nGuess #1: ")
        guess = guess.upper()

        # Checking to see if the word has been presolved
        presolved = False
        for word in presolved_words:
            if word[0] == guess:
                presolved = True
                presolved_feedback = word[1]
                continue

        # Provide the user with a list of predetermined "best" options, if requested
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
        if mode == "auto":
            input_word_into_wordle(guess)
        exit()


    else:
        if attempts == 1 and presolved == True:
            best_words = presolved_feedback[feedback][0]
            best_potential_answers = presolved_feedback[feedback][1]
        elif method == "1":
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
    if mode == "auto":
        input_word_into_wordle(guess)

    # The user then tells the computer what the feedback is from wordle, or they ask the computer for other word suggestions
    if mode == "play":
        feedback = provide_feedback()
    elif mode == "test":
        feedback = simulated_provide_feedback(secret_word, guess)
        print(f"Feedback: {feedback}")
    elif mode == "auto":
        feedback = get_feedback_automatically(attempts)
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
