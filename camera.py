import cv2
import numpy as np
from settings import COLOR

def camera_input(cap, use_camera_frame):
    if use_camera_frame:
        if not cap.isOpened():
            cap.open(0)
        ret, image = cap.read()

        image_flip = cv2.flip(image, 1)

        if COLOR is "BLUE":
            COLOR_MIN = np.array([90, 75, 25], np.uint8)
            COLOR_MAX = np.array([135, 255, 255], np.uint8)
        if COLOR is "GREEN":
            COLOR_MIN = np.array([45, 50, 25], np.uint8)
            COLOR_MAX = np.array([75, 255, 255], np.uint8)
        if COLOR is "PURPLE":
            COLOR_MIN = np.array([143, 50, 25], np.uint8)
            COLOR_MAX = np.array([165, 255, 255], np.uint8)

        new_image = cv2.cvtColor(image_flip, cv2.COLOR_BGR2HSV)

        image_threshold = cv2.inRange(new_image, COLOR_MIN, COLOR_MAX)

        contours, _ = cv2.findContours((image_threshold*255).astype(dtype=np.uint8), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)

        biggest = find_biggest_contour(contours)

        cv2.drawContours(image=image_flip, contours=biggest, contourIdx=-1, color=(255,255,255), thickness=-1)


        cv2.line(image_flip, (int(image_flip.shape[1] / 3), 0),
                 (int(image_flip.shape[1] / 3),image_flip.shape[0]),
                 (0,0,255), 2)
        cv2.line(image_flip, (int((image_flip.shape[1] / 3) * 2), 0),
                 (int((image_flip.shape[1] / 3) * 2), image_flip.shape[0]),
                 (0, 0, 255), 2)

        cv2.line(image_flip,(0, int(image_flip.shape[0] / 3)),
                 (image_flip.shape[1], int(image_flip.shape[0] / 3)),
                 (0,0,255), 2)

        cv2.line(image_flip, (0, int(image_flip.shape[0] / 3) * 2),
                 (image_flip.shape[1], int(image_flip.shape[0] / 3) * 2),
                 (0, 0, 255), 2)

        use_camera_frame = False
        return use_camera_frame, image_flip, biggest
    else:
        use_camera_frame = True
        return use_camera_frame, None, None


def find_biggest_contour(contours):
    min_area = 750

    biggest = None
    for c in range(len(contours)):
        contour = contours[c]
        if biggest is None:
            biggest = contour
        else:
            if cv2.contourArea(contour) > cv2.contourArea(biggest):
                biggest = contour

    area = -1
    if biggest is not None:
        area = cv2.contourArea(biggest)

    if area < min_area:
        biggest = None
    return biggest


def get_state(image, contour):
    if contour is not None:
        M = cv2.moments(contour)
        Cx = M['m10'] / M['m00']
        Cy = M['m01'] / M['m00']

        cv2.circle(img=image,
               center=(int(Cx), int(Cy)),
               radius=2,
               color=(0, 255, 0),
               thickness=-1)

        if int(Cx) < int(image.shape[1] / 3) and int(Cy) < int(image.shape[0] / 3):
            return "top_left"
        if (int(image.shape[1] / 3) * 2 > int(Cx) > int(image.shape[1] / 3)) and int(Cy) < int(image.shape[0] / 3):
            return "top"
        if int(Cx) > int(image.shape[1] / 3 * 2) and int(Cy) < int(image.shape[0] / 3):
            return "top_right"
        if int(Cx) < int(image.shape[1] / 3) and int(image.shape[0] / 3) * 2 > int(Cy) > int(image.shape[0] / 3):
            return "middle_left"
        if (int(image.shape[1] / 3) * 2 > int(Cx) > int(image.shape[1] / 3)) and int(image.shape[0] / 3) * 2 > int(Cy) > int(image.shape[0] / 3):
            return "middle"
        if int(Cx) > int(image.shape[1] / 3 * 2) and int(image.shape[0] / 3) * 2 > int(Cy) > int(image.shape[0] / 3):
            return "middle_right"
        if int(Cx) < int(image.shape[1] / 3) and int(Cy) > int(image.shape[0] / 3) * 2:
            return "bottom_left"
        if (int(image.shape[1] / 3) * 2 > int(Cx) > int(image.shape[1] / 3)) and int(Cy) > int(image.shape[0] / 3) * 2:
            return "bottom"
        if int(Cx) > int(image.shape[1] / 3 * 2) and int(Cy) > int(image.shape[0] / 3) * 2:
            return "bottom_right"
    else:
        return "none"



def close_game():
    c = cv2.waitKey(1)
    if c == 27:
        return True