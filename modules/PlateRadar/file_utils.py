import os
from modules.PlateRadar.Plate import *
from modules.PlateRadar.TrainingCharacter import *
import logging
from logging.config import fileConfig

fileConfig("logging_config.ini")
logger = logging.getLogger()

""" Loads all the images of cars from `/images/cars/` """


def load_images(folder):
    plates_array = []
    for image_filename in os.listdir(folder):
        logger.info("Loading image %s...", image_filename)
        image_file = cv2.imread(folder + image_filename)
        plate_object = Plate(image_file)
        plates_array.append(plate_object)
    return plates_array


""" Loads all the character training images from `images/characters` """


def load_characters(folder):
    characters_array = []
    for character in os.listdir(folder):
        logger.info("Loading character %s...", character)
        character_file = cv2.imread(folder + character)
        training_character_object = TrainingCharacter(character, character_file)
        characters_array.append(training_character_object)
    return characters_array
