from modules.PlateRadar.file_utils import *
from modules.PlateRadar.Plate import *
from modules.PlateRadar.TrainingCharacter import *
import logging
from logging.config import fileConfig

fileConfig("logging_config.ini")
logger = logging.getLogger()


def run():
    plates_array = load_images("images/cars/")
    characters_array = load_characters("images/characters/")
    logger.info("All testing images and characters have been downloaded.")

    for plate in plates_array:
        plate.plate_search(characters_array)

    logger.info("Finished plate recognition.")
    return True


run()
