import cv2
import numpy as np
from classes import CLASSES


def letterbox(img, new_shape=(640, 640), auto=False, scaleFill=False, scaleup=True, center=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        if center:
            dw /= 2  # divide padding into 2 sides
            dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)) if center else 0, int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)) if center else 0, int(round(dw + 0.1))
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )  # add border

        return img, ratio, dw, dh

def draw_box(img, 
             box,   # [xmin, ymin, xmax, ymax]
             score, 
             class_id):
    '''Draws a bounding box on the image'''

    # Retrieve the color for the class ID
    color_palette = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    color = color_palette[class_id]
    
    # Draw the bounding box on the image
    cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)

    # Create the label text with class name and score
    label = f'{CLASSES[class_id]}: {score:.2f}'

    # Calculate the dimensions of the label text
    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

    # Calculate the position of the label text
    label_x = box[0]
    label_y = box[1] - 10 if box[1] - 10 > label_height else box[1] + 10

    # Draw a filled rectangle as the background for the label text
    cv2.rectangle(
        img,
        (int(label_x), int(label_y - label_height)),
        (int(label_x + label_width), int(label_y + label_height)),
        color,
        cv2.FILLED,
    )

    # Draw the label text on the image
    cv2.putText(img, label, (int(label_x), int(label_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    return img