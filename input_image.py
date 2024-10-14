from PIL import Image
import json
import base64
import cv2
import numpy as np
import os

def load_gt_boxes(file):
    with open(f"images/poly_gt_{file}.txt", 'r') as src_file:
        contents = src_file.readlines()
    x = []
    y = []
    words = []
    boxes = []
    for content in contents:
        content = content.replace("  ", " ")
        parts = content.split(',')
        temp = parts[0].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")
        x_coords = []
        for i in temp:
            if i:
                x_coords.append(int(i))

        temp = parts[1].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")
        y_coords = []
        for i in temp:
            if i:
                y_coords.append(int(i))
        # y_coords = list(map(int, content.split(',')[1].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")))
        # print(x_coords, y_coords, list(zip(x_coords, y_coords)))
        word = parts[-1].split(":")[-1].strip().replace("[","").replace("]","").replace("u'","").replace("'","")
        # print(word)
        # if word == '#':
        #     word = '###'
        #     continue
        
        words.append(word)
        x.append(np.array(x_coords))
        y.append(np.array(y_coords))
        boxes.append(list(zip(x_coords, y_coords)))

    boxes2 = []
    # print(contents)
    try:
        tot_area = 0
        for content in contents:
            temp = content.split(',')[0].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")
            x_coords = []
            for i in temp:
                if i:
                    x_coords.append(int(i))

            temp = content.split(',')[1].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")
            y_coords = []
            for i in temp:
                if i:
                    y_coords.append(int(i))
            # y_coords = list(map(int, content.split(',')[1].split(":")[1].strip().replace("[", "").replace("]", "").split(" ")))
            boxes2.append(list(zip(x_coords, y_coords)))
        # print(boxes)
    except:
        print(content)
    return boxes, words


keys = ['version', 'flags', 'shapes', 'imagePath', 'imageData', 'imageHeight', 'imageWidth']

def random():
    d = {}
    with open('images/4.jpg', 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    data = json.load(open('images/3.json'))
    for k in keys:
        d[k] = data[k]

    d['imageData'] = img_base64
    img = cv2.imread("images/4.jpg")
    d['imageHeight'] = img.shape[0]
    d['imageWidth'] = img.shape[1]


    with open("images/4.json", 'w') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def tt():
    d = {}
    with open('images/img2.jpg', 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    data = json.load(open('images/3.json'))
    for k in keys:
        d[k] = data[k]

    d['imageData'] = img_base64
    img = cv2.imread("images/img2.jpg")
    d['imageHeight'] = img.shape[0]
    d['imageWidth'] = img.shape[1]

    shape_keys = list(d['shapes'][0].keys())
    shapes = []
    boxes, words = load_gt_boxes("img2")
    for box, word in zip(boxes, words):
        temp = {}
        temp['group_id'] = None
        temp['mask'] = None
        temp['description'] = "Select an option"
        temp['character'] = "Select an option"
        temp['shape_type'] = "polygon"
        temp['flags'] = {}
        temp['label'] = word
        temp['points'] = box
        shapes.append(temp)
    d['shapes'] = shapes

    with open("images/img2.json", 'w') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def calculate_num_points(distance):
    return max(0, int(distance // 20))

def add_intermediate_points(box):
    def interpolate(p1, p2, num_points):
        points = []
        for i in range(1, num_points + 1):
            ratio = i / (num_points + 1)
            x = p1[0] + ratio * (p2[0] - p1[0])
            y = p1[1] + ratio * (p2[1] - p1[1])
            points.append([x, y])
        return points

    new_points = []
    for i in range(len(box)):
        p1 = box[i]
        p2 = box[(i + 1) % len(box)]
        distance = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
        num_intermediate_points = calculate_num_points(distance)
        segment_length = distance / (num_intermediate_points + 1)
        new_points.append(p1)
        new_points.extend(interpolate(p1, p2, num_intermediate_points))
    return new_points

import math

def add_points_to_rectangle(points, image_width, image_height, base_points=1000):
    def distance(p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def interpolate(p1, p2, t):
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    
    def rectangle_area(pts):
        width = max(pts[0][0], pts[1][0], pts[2][0], pts[3][0]) - min(pts[0][0], pts[1][0], pts[2][0], pts[3][0])
        height = max(pts[0][1], pts[1][1], pts[2][1], pts[3][1]) - min(pts[0][1], pts[1][1], pts[2][1], pts[3][1])
        return width * height
    
    # Calculate the length of each side and total perimeter
    sides = [distance(points[i], points[(i+1)%4]) for i in range(4)]
    perimeter = sum(sides)
    
    # Calculate areas
    image_area = image_width * image_height
    rect_area = rectangle_area(points)
    
    # Calculate the number of points based on rectangle size relative to image
    area_ratio = rect_area / image_area
    total_points = int(base_points * area_ratio * (perimeter / math.sqrt(image_area)))
    
    # Ensure a minimum number of points
    total_points = max(total_points, 4)
    
    # Calculate the number of points to add to each side
    points_per_side = [round(side / perimeter * total_points) for side in sides]
    print(points, points_per_side, rect_area, image_area)
    
    result = []
    for i in range(4):
        p1, p2 = points[i], points[(i+1)%4]
        result.append(p1)
        
        for j in range(1, points_per_side[i]):
            t = j / (points_per_side[i] + 1)
            result.append(interpolate(p1, p2, t))
    
    return result


def add_points_to_rectangle(points, image_width, image_height, base_points=1000):
    def distance(p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def interpolate(p1, p2, t):
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    
    def rectangle_area(pts):
        width = max(pts[0][0], pts[1][0], pts[2][0], pts[3][0]) - min(pts[0][0], pts[1][0], pts[2][0], pts[3][0])
        height = max(pts[0][1], pts[1][1], pts[2][1], pts[3][1]) - min(pts[0][1], pts[1][1], pts[2][1], pts[3][1])
        return width * height
    
    # Calculate the length of each side and total perimeter
    sides = [distance(points[i], points[(i+1)%4]) for i in range(4)]
    perimeter = sum(sides)
    
    # Calculate areas
    image_area = image_width * image_height
    rect_area = rectangle_area(points)
    
    # Calculate the number of points based on rectangle size relative to image
    area_ratio = rect_area / image_area
    total_points = int(base_points * area_ratio * (perimeter / math.sqrt(image_area)))
    
    # Ensure a minimum number of points
    total_points = max(total_points, 8)  # Minimum 2 points per side (including vertices)
    
    # Calculate the number of segments for each side (number of spaces between points)
    segments_per_side = [max(1, round((side / perimeter * total_points) - 1)) for side in sides]
    
    result = []
    for i in range(4):
        p1, p2 = points[i], points[(i+1)%4]
        
        # Add points for this side, including both vertices
        for j in range(segments_per_side[i] + 1):
            t = j / segments_per_side[i]
            result.append(interpolate(p1, p2, t))
    
    return result

def indic(file):
    d = {}
    with open(f'images/Bengali/images/{file}', 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    data = json.load(open('images/3.json'))
    for k in keys:
        d[k] = data[k]

    d['imageData'] = img_base64
    img = cv2.imread(f'images/Bengali/images/{file}')
    d['imageHeight'] = img.shape[0]
    d['imageWidth'] = img.shape[1]
    image = cv2.imread(f'images/Bengali/images/{file}')

    filename = f'images/Bengali/images/{file[:-4]}_gt.json'
    try:
        f = open(filename)
    except:
        return

    data = json.load(f)
    words = data[0]['meta']['words']
    print("hello", file)
    shapes = []
    for word in words:
        x1, y1, w, h = list(word['bounding_box'].values())
        x2 = x1+w
        y2 = y1+h
        box = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        ar = (x1-x2)*(y1-y2)
        area = abs((x2 - x1) * (y2 - y1))
        num_points = calculate_num_points(area)
        # description = word['language_code']
        temp = {}
        # temp['points'] = add_intermediate_points(box, num_points)
        temp['points'] = add_points_to_rectangle(box, img.shape[1], img.shape[0])
        temp['group_id'] = None
        temp['mask'] = None
        temp['description'] = "Select an option" if not 'language_code' in word else word['language_code']
        temp['character1'] = "Select an option"
        temp['character2'] = "Select an option"
        temp['character3'] = "Select an option"
        temp['character4'] = "Select an option"
        temp['character5'] = "Select an option"
        temp['character6'] = "Select an option"
        temp['character7'] = "Select an option"
        temp['shape_type'] = "polygon"
        temp['flags'] = {}
        temp['label'] = word['text'] if 'text' in word else None
        # temp['points'] = box
        shapes.append(temp)
    
    d['shapes'] = shapes

    with open(f'images/{file[:-4]}.json', 'w') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    
    import shutil
    shutil.copy(f"images/Bengali/images/{file}", f"images/{file}")


files = sorted(os.listdir("images/Bengali/images"))
for file in files[400:500]:
    if file.endswith(".png"):
        indic(file)


# well lit, poor illumination, light exposure
# horizontal, vertical, multioriented
# horizontal curved, vertical curved, circular curved, wavy curved
# non occluded, occluded
# 2d Text, 3d Text
# normal, perspective
# which are occlusion attribute, complex background attribute, distortion attribute, raised attribute, wordart attribute, and handwritten attribute.