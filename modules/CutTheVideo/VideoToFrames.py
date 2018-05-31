import time
import cv2
import os
import json

""" This function is used to extract frames from video,
we will use it in order to extract cars pictures from the whole video.
The arguments are, video location, output location and buffer: 
1 of how many frames to take 
"""


def capture_video_frames(video_location, output_location, buffer):
    """
    Setting the start time for calculating the duration of the function,
    it might be useful for later in case we will have to improve performances
    so we monitor everything now
    """
    start_time = time.time()
    # Capturing the video feed
    feed_cap = cv2.VideoCapture(video_location)
    print("Creating dir for output \n")
    try:
        os.mkdir(output_location)
    except OSError:
        pass

    # Find and log the amount of frames
    video_length = int(feed_cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("Number of frames: ", video_length)
    count = 0
    print("Starting conversion process\n")

    # Start converting the video
    while feed_cap.isOpened():
        # Extract specific frame
        ret, curr_frame = feed_cap.read()

        # Set 1 of how many frames do we want to capture
        if count % buffer == 0:
            # Write the results back to output location in the following format: 00001, 00020 and etc'.
            cv2.imwrite(output_location + "/%#05d.jpg" % (count + 1), curr_frame)
        count += 1

        # Checking if there are more frames
        if count > (video_length - 1):
            print("The process was finished successfully.\n")
            # Get the end time and release the feed
            feed_cap.release()
            end_time = time.time()

            print("%d frames extracted" % count)
            print("The whole process took %d seconds." % (end_time - start_time))
            break


# Reading the configuration file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)

capture_video_frames(data['other']['video_location_config'], data['other']['output_location_config'],
                     data['other']['buffer_config'])
