import pytesseract as tes
from PIL import Image
from modules.PlateRadar.TrainingCharacter import *
from matplotlib import pyplot as plt
from copy import deepcopy
from logging.config import fileConfig

# logger setup
fileConfig("logging_config.ini")
logger = logging.getLogger()


class Plate:
    """ Class for the license plates """

    def __init__(self, image):  # Plate Class Vars #
        self.original_image = image  # original image of analysis
        self.plate_located_image = deepcopy(image)  # original image with plate highlighted
        self.plate_image = None  # license plate cropped
        self.plate_image_char = None  # license plate cropped, chars outlined
        self.gray_image = None  # original image - gray scale for analysis
        self.plate_number = ""  # plate number
        self.roi = []  # regions of interest for plates
        self.plate_characters = []  # cropped images of characters on plate
        logger.info("New plate created.")

    """ Converts original image to gray scale for analysis """

    def gray_image(self, image):
        logger.info("Image converted to gray scale")
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    """ Algorithm to find plate and read characters """

    def plate_search(self, characters_array):
        self.find_contour()
        self.crop_plate()
        if self.plate_image is not None:
            self.read_plate_number(characters_array)
        self.show_results()
        return True

    """ Searches for a contour that looks like a license plate
    in the image of a car """

    def find_contour(self):
        self.gray_image = self.gray_image(deepcopy(self.original_image))
        self.gray_image = cv2.medianBlur(self.gray_image, 5)

        self.gray_image = cv2.adaptiveThreshold(self.gray_image,
                                                255,
                                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY,
                                                43,
                                                2)
        _, contours, _ = cv2.findContours(self.gray_image,
                                          cv2.RETR_TREE,
                                          cv2.CHAIN_APPROX_SIMPLE)

        w, h, x, y = 0, 0, 0, 0

        for contour in contours:
            area = cv2.contourArea(contour)

            # rough range of areas of a license plate
            if 6000 < area < 40000:
                [x, y, w, h] = cv2.boundingRect(contour)

            # rough dimensions of a license plate
            if 100 < w < 200 and 60 < h < 100:
                self.roi.append([x, y, w, h])
                cv2.rectangle(self.plate_located_image,
                              (x, y),
                              (x + w, y + h),
                              (0, 255, 0), 10)
        logger.info("%s potential plates found.", str(len(self.roi)))

        return True

    """ If a license plate contour has been found, crop
    out the contour and create a new image """

    def crop_plate(self):
        if len(self.roi) > 1:
            [x, y, w, h] = self.roi[0]
            self.plate_image = self.original_image[y:y + h, x:x + w]
            self.plate_image_char = deepcopy(self.plate_image)
        return True

    """ Subalgorithm to read the license plate number using the
    cropped image of a license plate """

    def read_plate_number(self, characters_array):
        self.find_character_contour()
        self.tesseract_character()
        return True

    """ Crops individual characters out of a plate image 
    and converts it to grayscale for comparison """

    def crop_character(self, dimensions):
        [x, y, w, h] = dimensions
        character = deepcopy(self.plate_image)
        character = deepcopy(character[y:y + h, x:x + w])
        return character

    """ Finds contours in the cropped image of a license plate
    that fit the dimension range of a letter or number """

    def find_character_contour(self):
        gray_plate = self.gray_image(deepcopy(self.plate_image))
        gray_plate = cv2.GaussianBlur(gray_plate, (3, 3), 0)

        _, threshold = cv2.threshold(gray_plate, 140, 255, 0)
        _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        w, h, x, y = 0, 0, 0, 0

        logger.info("%s contours found.", str(len(contours)))
        for contour in contours:
            area = cv2.contourArea(contour)

            # rough range of areas of a plate number
            if 120 < area < 2000:
                [x, y, w, h] = cv2.boundingRect(contour)

            # rough dimensions of a character
            if 20 < h < 90 and 10 < w < 50:
                character = self.crop_character([x, y, w, h])
                self.plate_characters.append([x, character])
                cv2.rectangle(self.plate_image_char,
                              (x, y),
                              (x + w, y + h),
                              (0, 0, 255),
                              1)

        logger.info("%s plate characters found", str(len(self.plate_characters)))
        return True

    """ Tesseract: reads the character using the Tesseract library """

    def tesseract_character(self):
        self.plate_characters = sorted(self.plate_characters, key=lambda x: x[0])  # sort contours left to right
        for character in self.plate_characters[:8]:  # only first 8 contours
            char_image = Image.fromarray(character[1])
            char = tes.image_to_string(char_image, config='-psm 10')
            self.plate_number += char.upper()
        return True

    """ Subplot generator for images """

    def plot(self, figure, subplot, image, title):
        figure.subplot(subplot)
        figure.imshow(image)
        figure.xlabel(title)
        figure.xticks([])
        figure.yticks([])
        return True

    """ Show our results """

    def show_results(self):
        plt.figure(self.plate_number)

        self.plot(plt, 321, self.original_image, "Original image")
        self.plot(plt, 322, self.gray_image, "Threshold image")
        self.plot(plt, 323, self.plate_located_image, "Plate located")

        if self.plate_image is not None:
            self.plot(plt, 324, self.plate_image, "License plate")
            self.plot(plt, 325, self.plate_image_char, "Characters outlined")
            plt.subplot(326)
            plt.text(0, 0, self.plate_number, fontsize=30)
            plt.xticks([])
            plt.yticks([])
        plt.tight_layout()
        plt.show()
        return True