#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import datetime
import os
import numpy as np
import cv2
from utils import draw_box, letterbox
from tqdm import tqdm

from acllite_resource import AclLiteResource
from acllite_model import AclLiteModel
from acllite_imageproc import AclLiteImageProc
from acllite_image import AclLiteImage
from acllite_logger import log_error, log_info


class SampleYOLOV10(object):
    '''load the model, and do preprocess, infer, postprocess'''
    def __init__(self, model_path, model_width, model_height):
        self.model_path = model_path
        self.model_width = model_width
        self.model_height = model_height
        self.resource = None
        self.dvpp = None
        self.model = None

    def init_resource(self):
        # initial acl resource, create image processor, create model
        try:
            self.resource = AclLiteResource()
            self.resource.init()
            self.dvpp = AclLiteImageProc(self.resource)
            self.model = AclLiteModel(self.model_path)
        except Exception as e:
            log_error(f"Failed to initialize resources: {e}")

    def preprocess(self, image):
        image, self.ratio, self.dw, self.dh = letterbox(image, new_shape=(self.model_width, self.model_height))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.transpose(image, (2, 0, 1))
        image = image.astype(np.float32) / 255.0
        self.input_tensor = np.expand_dims(image, axis=0)
        return self.input_tensor, self.ratio, self.dw, self.dh

    def infer(self):
        # infer frame
        self.output = self.model.execute([self.input_tensor])
        self.output = np.squeeze(self.output[0])
        return self.output
    
    def postprocess(self):
        result = []
        for i in range(self.output.shape[0]):
            # 读取类别置信度
            confidence = self.output[i][4]
            # 用阈值进行过滤
            if confidence > 0.5:
                # 读取类别索引
                label = int(self.output[i][5])
                # 读取类坐标值，把坐标还原到原始图像
                xmin = int((self.output[i][0] - int(round(self.dw - 0.1))) / self.ratio[0])
                ymin = int((self.output[i][1] - int(round(self.dh - 0.1))) / self.ratio[1])
                xmax = int((self.output[i][2] - int(round(self.dw + 0.1))) / self.ratio[0])
                ymax = int((self.output[i][3] - int(round(self.dh + 0.1))) / self.ratio[1])
                result.append([xmin, ymin, xmax, ymax, confidence, label])

        return result

    def release_resource(self):
        # release resource includes acl resource, data set and unload model
        if self.resource:
            del self.resource
        if self.dvpp:
            del self.dvpp
        if self.model:
            del self.model

def image_infer(img_path, model, output_folder):
    """Detect objects in an image using YOLOv10 and save the annotated image."""
    frame = cv2.imread(img_path)
    time0 = datetime.datetime.now()
    model.preprocess(frame)
    time1 = datetime.datetime.now()
    model.infer()
    time2 = datetime.datetime.now()
    result = model.postprocess()
    time3 = datetime.datetime.now()
    
    log_info(f"preprocess time: {(time1 - time0).total_seconds() * 1000} ms")
    log_info(f"infer time: {(time2 - time1).total_seconds() * 1000} ms")
    log_info(f"postprocess time: {(time3 - time2).total_seconds() * 1000} ms")    
    # 可视化
    for xmin, ymin, xmax, ymax, confidence, label in result:
        draw_box(frame, [xmin, ymin, xmax, ymax], confidence, label)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(img_path))[0]}-{timestamp}.jpg')
    cv2.imwrite(output_path, frame)

def video_infer(video_path, model, output_folder):
    """Detect objects in a video using YOLOv10 and save the annotated video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Error opening video file")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create VideoWriter object to write the output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_path = os.path.join(output_folder, f'output-{timestamp}.mp4')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    preprocess_time = 0
    infer_time = 0
    postprocess_time = 0
    with tqdm(total=total_frames, desc="Processing frames", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            time0 = datetime.datetime.now()
            model.preprocess(frame)
            time1 = datetime.datetime.now()
            model.infer()
            time2 = datetime.datetime.now()
            result = model.postprocess()
            time3 = datetime.datetime.now()

            preprocess_time += (time1 - time0).total_seconds()
            infer_time += (time2 - time1).total_seconds()
            postprocess_time += (time3 - time2).total_seconds()

            for xmin, ymin, xmax, ymax, confidence, label in result:
                draw_box(frame, [xmin, ymin, xmax, ymax], confidence, label)

            out.write(frame)  # Write the processed frame to the output video
            pbar.update(1)  # Update the progress bar

        cap.release()
        out.release()  # Release the VideoWriter
    log_info(f"preprocess time: {preprocess_time * 1000} ms")
    log_info(f"infer time: {infer_time * 1000} ms")
    log_info(f"postprocess time: {postprocess_time * 1000} ms")

def main():
    input_folder = 'data'
    output_folder = 'outputs'
    model = SampleYOLOV10('./models/yolov10n_310B4.om', 640, 640)
    model.init_resource()

    mode = "image"
    if mode == "image":
        image_path = os.path.join(input_folder, 'bus.jpg')
        image_infer(image_path, model, output_folder)
    elif mode == "video":
        video_path = os.path.join(input_folder, 'test.mp4')
        video_infer(video_path, model, output_folder)
    else:
        print('input mode is incorrect.')

    model.release_resource()


if __name__ == '__main__':
    main()
