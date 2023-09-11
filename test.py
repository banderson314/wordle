import cv2
import numpy as np
import pyautogui

def display_image(image, wait_time=10_000):
    cv2.imshow(f"Image: {image}", image)
    cv2.waitKey(wait_time)
    cv2.destroyAllWindows()

def print_list(list):
    for item in list:
        print(item)

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
    if area > 2000:
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
    display_image(image_with_contours)
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


# Get the RGB color at each coordinate in the first row
colors = []
first_row = row_coordinates[0]
for column in column_coordinates:
    pixel_color = pyautogui.pixel(column, first_row)
    colors.append(pixel_color)

#for coord in coordinates:
#    x, y = coord
#    pixel_color = pyautogui.pixel(x, y)
#    colors.append(pixel_color)

def rgb_to_color_name(rgb):
    possible_colors = {
        "Yellow": (255, 255, 0),
        "Green": (0, 128, 0),
        "Black": (0, 0, 0),
        #"Gray": (128, 128, 128),
        "White": (255, 255, 255),
    }

    # Find the closest matching  color
    min_distance = float('inf')
    closest_color = None

    for color, possible_rgb in possible_colors.items():
        r1, g1, b1 = rgb
        r2, g2, b2 = possible_rgb
        distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

        if distance < min_distance:
            min_distance = distance
            closest_color = color

    return closest_color


print(colors)
colors = [rgb_to_color_name(rgb) for rgb in colors]



print(colors)
exit()

# Now 'grid_coordinates' contains the coordinates of the grid squares
print_list(grid_coordinates)
print(f"Row coordinates: {row_coordinates}")
print(f"Column coordinates: {column_coordinates}")
