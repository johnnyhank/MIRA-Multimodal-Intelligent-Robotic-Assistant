#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import cv2
import numpy as np
import onnxruntime as ort
from utils import draw_box, letterbox


class YOLOv10:
    def __init__(self, model_path):
        self.model_path = model_path
        self.session = ort.InferenceSession(self.model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape

    def preprocess(self, image, dst_w, dst_h):
        image, ratio, dw, dh = letterbox(image, new_shape=(dst_w, dst_h))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.transpose(image, (2, 0, 1))
        image = image.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(image, axis=0)

        return input_tensor, ratio, dw, dh
    
    def detect(self, input_tensor):
        outputs = self.session.run(None, {self.input_name: input_tensor})
        output = np.squeeze(outputs)
        return output
    
    def postprocess(self, output, ratio, dw, dh):
        result = []
        for i in range(output.shape[0]):
            # 读取类别置信度
            confidence = output[i][4]
            # 用阈值进行过滤
            if confidence > 0.5:
                # 读取类别索引
                label = int(output[i][5])
                # 读取类坐标值，把坐标还原到原始图像
                xmin = int((output[i][0] - int(round(dw - 0.1))) / ratio[0])
                ymin = int((output[i][1] - int(round(dh - 0.1))) / ratio[1])
                xmax = int((output[i][2] - int(round(dw + 0.1))) / ratio[0])
                ymax = int((output[i][3] - int(round(dh + 0.1))) / ratio[1])
                result.append([xmin, ymin, xmax, ymax, confidence, label])

        return result

if __name__ == '__main__':
    yolov10n = YOLOv10('models/yolov10m.onnx')
    img = cv2.imread('data/test.jpg')
    input_tensor, ratio, dw, dh = yolov10n.preprocess(img, yolov10n.input_shape[3], yolov10n.input_shape[2])
    output = yolov10n.detect(input_tensor)
    result = yolov10n.postprocess(output, ratio, dw, dh)
    
    # 可视化
    for xmin, ymin, xmax, ymax, confidence, label in result:
        draw_box(img, [xmin, ymin, xmax, ymax], confidence, label)

    cv2.imwrite('result.jpg', img)
    print('save done')
