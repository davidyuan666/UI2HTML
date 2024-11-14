# -*- coding = utf-8 -*-
# @time:2024/8/21 18:53
# Author:david yuan
# @File:edge_convert.py
# @Software:VeSync


import cv2
import pytesseract
from pytesseract import Output
import os
import json
from webpage_handler import WebpageHandler
import platform
from bs4 import BeautifulSoup
import difflib
import html5lib
from zss import simple_distance, Node
from bs4 import BeautifulSoup
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def get_vector(html):
    soup = BeautifulSoup(html, 'html.parser')
    tags = [tag.name for tag in soup.find_all()]
    vector = Counter(tags)
    return vector

def cosine_sim(vec1, vec2):
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]
def get_tree(html):
    dom = html5lib.parse(html)
    return dom

def to_zss_node(node):
    zss_node = Node(node.tag)
    for child in node:
        zss_node.addkid(to_zss_node(child))
    return zss_node


'''
pip install opencv-python pytesseract
'''
def main(image_path,output_image_path):
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Otsu's thresholding to binarize the image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes around the detected text
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Save the processed image
    cv2.imwrite(output_image_path, image)

    # Display the image
    cv2.imshow('Processed Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main_v2(input_image_path,output_image_path):
    import cv2
    import pytesseract
    import json

    image = cv2.imread(input_image_path)

    # Convert the image to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract bounding boxes and text information
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(gray, output_type=Output.DICT, config=custom_config)

    # Prepare data to be saved in JSON format
    text_data = []
    for i in range(len(details['text'])):
        if int(details['conf'][i]) > 30:  # Confidence threshold to filter weak detections
            x, y, w, h = details['left'][i], details['top'][i], details['width'][i], details['height'][i]
            text = details['text'][i]
            text_data.append({"bounding_box": {"x": x, "y": y, "w": w, "h": h}, "text": text})


    json_data = json.dumps(text_data, indent=4)

    # Save JSON data to a file
    json_file_path =output_image_path
    with open(json_file_path, 'w') as file:
        file.write(json_data)

    print("JSON data has been saved to", json_file_path)

    webpage = WebpageHandler()
    json_data = json_data
    response = webpage.chat(json_data)
    print(response)


def main_v3(input_image_path):
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # default for Unix-like systems

    image = cv2.imread(input_image_path)

    # Convert the image to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract bounding boxes and text information
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=custom_config)

    # Prepare data to be saved in JSON format
    text_data = []
    for i in range(len(details['text'])):
        if int(details['conf'][i]) > 30:  # Confidence threshold to filter weak detections
            x, y, w, h = details['left'][i], details['top'][i], details['width'][i], details['height'][i]
            text = details['text'][i]
            text_data.append({"bounding_box": {"x": x, "y": y, "w": w, "h": h}, "text": text})

    json_data = json.dumps(text_data, indent=4)

    # Initialize the WebpageHandler
    webpage = WebpageHandler()

    # Generate and save HTML page using the OCR data
    response = webpage.chat(json_data)
    print(response)

    # Save the response to a file instead of printing it
    with open('example_ui_images/response.txt', 'w') as file:
        file.write(response)



def main_v5(input_image_path):
    cot_prompts = [
        'Tree of Thought: Structure reasoning in a hierarchical tree format for complex layouts. Utilize this thought model to consider how to generate HTML and CSS from JSON.',
        'Graph of Thought: Utilize graph-based reasoning to understand and connect disparate UI elements. Apply this thought model to consider how to generate HTML and CSS from JSON.',
        'Table of Thought: Organize and analyze UI components using tabular interpretations. Use this thought model to consider how to generate HTML and CSS from JSON.'
    ]

    # Set the path for Tesseract based on operating system
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Default for Unix-like systems

    # Load the image and convert to grayscale
    image = cv2.imread(input_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract bounding boxes and text information
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=custom_config)

    # Filter results and structure data for JSON
    text_data = []
    for i in range(len(details['text'])):
        if int(details['conf'][i]) > 30:  # Consider only confident results
            x, y, w, h = details['left'][i], details['top'][i], details['width'][i], details['height'][i]
            text = details['text'][i]
            text_data.append({"bounding_box": {"x": x, "y": y, "w": w, "h": h}, "text": text})

    json_data = json.dumps(text_data, indent=4)

    # Generate HTML and CSS using different CoT prompts
    for index, prompt in enumerate(cot_prompts, 1):
        webpage = WebpageHandler(prompt)
        response = webpage.chat(json_data)
        print(response)

        # Save each response to a unique file
        with open(f'response_{index}.txt', 'w') as file:
            file.write(response)


def baseline_chat():
    cot_prompts = [
        'Tree of Thought: Structure reasoning in a hierarchical tree format for complex layouts. Utilize this thought model to consider how to generate HTML and CSS from JSON.',
        'Graph of Thought: Utilize graph-based reasoning to understand and connect disparate UI elements. Apply this thought model to consider how to generate HTML and CSS from JSON.',
        'Table of Thought: Organize and analyze UI components using tabular interpretations. Use this thought model to consider how to generate HTML and CSS from JSON.'
    ]

    for index, prompt in enumerate(cot_prompts, 1):
        webpage = WebpageHandler(prompt)
        generated_html = webpage.image_chat('according to the image UI and generate HTML and CSS from image',
                                      os.path.join(os.getcwd(), 'example_ui_images', 'img.png'))

        # Save each response to a unique file
        with open(f'base_experiment_response_{index}.txt', 'w') as file:
            file.write(generated_html)




def main_v6(input_image_path):
    cot_prompts = [
        'Tree of Thought: Structure reasoning in a hierarchical tree format for complex layouts. Utilize this thought model to consider how to generate HTML and CSS from JSON.',
        'Graph of Thought: Utilize graph-based reasoning to understand and connect disparate UI elements. Apply this thought model to consider how to generate HTML and CSS from JSON.',
        'Table of Thought: Organize and analyze UI components using tabular interpretations. Use this thought model to consider how to generate HTML and CSS from JSON.'
    ]

    original_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>Bootstrap Example</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    </head>
    <body>

    <div class="jumbotron text-center">
      <h1>My First Bootstrap Page</h1>
      <p>Resize this responsive page to see the effect!</p> 
    </div>

    <div class="container">
      <div class="row">
        <div class="col-sm-4">
          <h3>Column 1</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
        <div class="col-sm-4">
          <h3>Column 2</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
        <div class="col-sm-4">
          <h3>Column 3</h3>        
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
      </div>
    </div>

    </body>
    </html>
    """

    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Default for Unix-like systems

    image = cv2.imread(input_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=custom_config)

    text_data = []
    for i in range(len(details['text'])):
        if int(details['conf'][i]) > 30:
            x, y, w, h = details['left'][i], details['top'][i], details['width'][i], details['height'][i]
            text = details['text'][i]
            text_data.append({"bounding_box": {"x": x, "y": y, "w": w, "h": h}, "text": text})

    json_data = json.dumps(text_data, indent=4)

    for index, prompt in enumerate(cot_prompts, 1):
        webpage = WebpageHandler(prompt)
        generated_html = webpage.chat(json_data)

        # Compare the original and generated HTML content
        original_soup = BeautifulSoup(original_html, 'html.parser')
        generated_soup = BeautifulSoup(generated_html, 'html.parser')

        # Calculate similarity
        text1 = original_soup.get_text(strip=True)
        text2 = generated_soup.get_text(strip=True)
        similarity_score = difflib.SequenceMatcher(None, text1, text2).ratio()

        print(f'Similarity score between original and generated HTML (Experiment {index}): {similarity_score}')

        # Save each response to a unique file
        with open(f'experiment_response_{index}.html', 'w') as file:
            file.write(generated_html)

def calculate_difference_webpage():
    prompt = 'Convert the input into HTML format only without any other information, just return HTML format'
    webpage = WebpageHandler(prompt)

    original_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>Bootstrap Example</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    </head>
    <body>

    <div class="jumbotron text-center">
      <h1>My First Bootstrap Page</h1>
      <p>Resize this responsive page to see the effect!</p> 
    </div>

    <div class="container">
      <div class="row">
        <div class="col-sm-4">
          <h3>Column 1</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
        <div class="col-sm-4">
          <h3>Column 2</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
        <div class="col-sm-4">
          <h3>Column 3</h3>        
          <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit...</p>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...</p>
        </div>
      </div>
    </div>

    </body>
    </html>
    """

    generated_html_path = os.path.join(os.getcwd(),'example_ui_images','response.txt')

    if os.path.exists(generated_html_path):
        with open(generated_html_path, 'r') as file:
            generated_html = file.read()

        # generated_html = webpage.chat(generated_html)

        # print(f'generated html: {generated_html}')

        original_soup = BeautifulSoup(original_html, 'html.parser')
        generated_soup = BeautifulSoup(generated_html, 'html.parser')

        text1 = original_soup.get_text(strip=True)
        text2 = generated_soup.get_text(strip=True)
        similarity_score = difflib.SequenceMatcher(None, text1, text2).ratio()
        print(f'text Similarity Score: {similarity_score}')

        # Use prettify to get a string that includes tags
        text1 = original_soup.prettify()
        text2 = generated_soup.prettify()

        similarity_score = difflib.SequenceMatcher(None, text1, text2).ratio()
        print(f'tag Similarity Score: {similarity_score}')

        original_tree = get_tree(original_html)
        generated_tree = get_tree(generated_html)

        original_zss_tree = to_zss_node(original_tree)
        generated_zss_tree = to_zss_node(generated_tree)

        distance = simple_distance(original_zss_tree, generated_zss_tree)

        print(f'tree distance Similarity distance: {distance}')  # prints the tree edit distance

        vec1 = get_vector(original_html)
        vec2 = get_vector(generated_html)

        vectorizer = CountVectorizer().fit_transform([str(vec1), str(vec2)])
        vectors = vectorizer.toarray()

        csim = cosine_sim(vectors[0], vectors[1])

        print(f'vector Similarity distance: {csim}')  # prints the tree edit distance

    else:
        print("Generated HTML file not found. Please check the path or generation process.")


'''
html text Similarity Score: 0.0979381443298969
html tag Similarity Score: 0.09707309898514488
html tree distance Similarity distance: 59.0 # 为 ZSS（Zhang-Shasha algorithm）可以处理的格式。ZSS 是一种用于计算树编辑距离的算法。
html vector Similarity distance: 0.8040302522073697
'''

if __name__ == '__main__':
    image_path = os.path.join(os.getcwd(), 'example_ui_images','img.png')
    output_image_path =os.path.join(os.getcwd(), 'example_ui_images','out_img_v2.json')
    # main_v2(image_path,output_image_path)
    # main_v3(input_image_path=image_path)
    # main_v5(input_image_path=image_path)
    # main_v6(input_image_path=image_path)
    # baseline_chat()
    calculate_difference_webpage()