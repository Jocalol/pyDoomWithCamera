import cv2
from ultralytics import YOLO

model = YOLO("yolov8m.pt")

def camera_input(cap, use_camera_frame):
    if use_camera_frame:
        if not cap.isOpened():
            cap.open(0)
        ret, image = cap.read()

        image_flip = cv2.flip(image, 1)

        # convert image to RGB because the model is only trained to deal with those
        image_RGB = cv2.cvtColor(image_flip, cv2.COLOR_BGR2RGB)

        # get the results from the model
        results = model(image_RGB, verbose=False)

        #get the objects from the results the model gave
        objects = results[0]

        #initialize the rectangle for the object outside the loop for convenience
        object_rect = None

        #go through every object and check for scissors
        for object in objects:

            #get the object box's properties (coordinates, confidence, and the type of object)
            (x1, y1, x2, y2, conf, class_id) = object.boxes.data[0]

            if model.names[int(class_id)] == "scissors":

                #get the rectangle from the scissors and draw it
                object_rect = [x1, x2, y1, y2]

                cv2.rectangle(img=image_flip,
                          pt1=(int(x1), int(y1)),
                          pt2=(int(x2), int(y2)),
                          color=(0, 255, 0),
                          thickness=2)

                #show confidence for debugging purposes
                object_text = "{:.2f}".format(conf)
                cv2.putText(image_flip,
                        object_text,
                        org=(int(x1), int(y1)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0),
                        thickness=1,
                            lineType=cv2.LINE_AA
                        )



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
        return use_camera_frame, image_flip, object_rect
    else:
        use_camera_frame = True
        return use_camera_frame, None, None

def get_state(image, box):
    if box is not None:

        #get the center of the box
        Cx = int((box[0]+box[1])/2)
        Cy = int(box[2]+box[3]/2)

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