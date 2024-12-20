import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8m.pt")

def camera_input(cap, use_camera_frame, roi_hist, track_window, term_crit, pad):
    if use_camera_frame:
        if not cap.isOpened():
            cap.open(0)
        ret, image = cap.read()

        image_flip = cv2.flip(image, 1)

        new_roi_hist = roi_hist

        if ret:
            hsv = cv2.cvtColor(image_flip, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], new_roi_hist, [0, 180], 1)

            # apply camshift to get the new location
            ret, track_window = cv2.meanShift(dst, track_window, term_crit)

            # Draw it on image
            x, y, w, h = track_window
            image_flip = cv2.rectangle(image_flip, (x, y), (x + w, y + h), 255, 2)

            k = cv2.waitKey(30) & 0xff


            if k == ord('a'):
                print(str(track_window[0]) + ' ' + str(track_window[1]) + " " + str(track_window[2]) + ' ' + str(track_window[3]))
            elif k == ord('q'):
                cv2.waitKey()
                first_pos = (pad[0], pad[1])

                if pad[2] > pad[0] and pad[3] > pad[1]:
                    second_pos = (pad[2] - pad[0], pad[3] - pad[1])

                    track_window = (first_pos[0], first_pos[1], second_pos[0], second_pos[1])

                    print(str(first_pos) + "hello" + str(second_pos))
                    roi = image_flip[y:y + h, x:x + w]
                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
                    new_roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])


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
        return use_camera_frame, image_flip, track_window, new_roi_hist
    else:
        use_camera_frame = True
        return use_camera_frame, None, track_window, roi_hist

def get_state(image, track_window):
    if track_window is not None:

        #get the center of the box
        Cx = int(((track_window[0]+track_window[2])+track_window[0])/2)
        Cy = int((track_window[1]+(track_window[1]+track_window[3]))/2)

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