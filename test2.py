import pyautogui

# Capture a screenshot of the area containing the square
screenshot = pyautogui.screenshot()

# Save the screenshot (optional)
#screenshot.save("screenshot.png")

# Wait for you to click the top-left corner of the square
print("Move the mouse cursor to the top-left corner of the square and press Enter...")
input()  # Wait for you to press Enter
top_left = pyautogui.position()
print("Top-left corner selected at position:", top_left)

# Wait for you to click the bottom-right corner of the square
print("Move the mouse cursor to the bottom-right corner of the square and press Enter...")
input()  # Wait for you to press Enter
bottom_right = pyautogui.position()
print("Bottom-right corner selected at position:", bottom_right)

# Calculate the width and height of the selected region
square_width = abs(bottom_right[0] - top_left[0])
square_height = abs(bottom_right[1] - top_left[1])

# Calculate the area of the square
square_area = square_width * square_height

print(f"Square Area: {square_area} square pixels")
