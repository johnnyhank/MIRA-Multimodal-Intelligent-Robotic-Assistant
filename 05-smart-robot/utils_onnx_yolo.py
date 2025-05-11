import threading
from threading import main_thread

import onnxruntime
from PIL import Image
import cv2
import numpy as np
import matplotlib as plt
import random

CLASSES = ['redapple','greenapple','pear','orange','peach']  # coco80类别


# NMS非极大值抑制
# dets:  array [x,6] 6个值分别为x1,y1,x2,y2,score,class
# thresh: 阈值
def nms(dets, thresh):
    # dets:x1 y1 x2 y2 score class
    # x[:,n]就是取所有集合的第n个数据
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    # 计算框的面积，置信度从大到小排序
    areas = (y2 - y1 + 1) * (x2 - x1 + 1)
    scores = dets[:, 4]
    # print(scores)
    keep = []
    index = scores.argsort()[::-1]  # np.argsort()对某维度从小到大排序

    while index.size > 0:
        i = index[0]
        keep.append(i)
        # 计算相交面积
        x11 = np.maximum(x1[i], x1[index[1:]])
        y11 = np.maximum(y1[i], y1[index[1:]])
        x22 = np.minimum(x2[i], x2[index[1:]])
        y22 = np.minimum(y2[i], y2[index[1:]])

        w = np.maximum(0, x22 - x11 + 1)
        h = np.maximum(0, y22 - y11 + 1)

        overlaps = w * h
        # 计算该框与其它框的IOU
        ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
        idx = np.where(ious <= thresh)[0]
        index = index[idx + 1]
    return keep


def xywh2xyxy(x):
    # [x, y, w, h] to [x1, y1, x2, y2]
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2
    y[:, 1] = x[:, 1] - x[:, 3] / 2
    y[:, 2] = x[:, 0] + x[:, 2] / 2
    y[:, 3] = x[:, 1] + x[:, 3] / 2
    return y


# 过滤掉无用的框
def filter_box(org_box, conf_thres, iou_thres):
    # -------------------------------------------------------
    #   删除为1的维度
    #	删除置信度小于conf_thres的BOX
    # -------------------------------------------------------
    org_box = np.squeeze(org_box)  # 删除数组形状中单维度条目(shape中为1的维度)
    # (25200, 9)
    # […,4]：代表了取最里边一层的所有第4号元素，…代表了对:,:,:,等所有的的省略。此处生成：25200个第四号元素组成的数组
    conf = org_box[..., 4] > conf_thres  # 0 1 2 3 4 4是置信度，只要置信度 > conf_thres 的
    box = org_box[conf == True]  # 根据objectness score生成(n, 9)，只留下符合要求的框

    # print('box:符合要求的框')
    # print(box.shape)

    # 通过argmax获取置信度最大的类别
    cls_cinf = box[..., 5:]  # 左闭右开（5 6 7 8），就只剩下了每个grid cell中各类别的概率
    cls = []
    for i in range(len(cls_cinf)):
        cls.append(int(np.argmax(cls_cinf[i])))  # 剩下的objecctness score比较大的grid cell，分别对应的预测类别列表
    all_cls = list(set(cls))  # 去重，找出图中都有哪些类别
    # set() 函数创建一个无序不重复元素集，可进行关系测试，删除重复数据。
    output = []
    for i in range(len(all_cls)):
        curr_cls = all_cls[i]
        curr_cls_box = []
        curr_out_box = []

        for j in range(len(cls)):
            if cls[j] == curr_cls:
                box[j][5] = curr_cls
                curr_cls_box.append(box[j][:6])  # 左闭右开，0 1 2 3 4 5

        curr_cls_box = np.array(curr_cls_box)  # 0 1 2 3 4 5 分别是 x y w h score class

        curr_cls_box = xywh2xyxy(curr_cls_box)  # 0 1 2 3 4 5 分别是 x1 y1 x2 y2 score class
        curr_out_box = nms(curr_cls_box, iou_thres)  # 获得nms后，剩下的类别在curr_cls_box中的下标

        for k in curr_out_box:
            output.append(curr_cls_box[k])
    output = np.array(output)
    return output


# 画框
def draw(image, box_data,target_name="redapple"):
    boxes = box_data[..., :4].astype(np.int32)  # x1 x2 y1 y2
    scores = box_data[..., 4]
    classes = box_data[..., 5].astype(np.int32)
    target_list = {}
    index = 0
    for box, score, cl in zip(boxes, scores, classes):
        #top
        left, top, right, bottom = box

        #打印置信度与边界框的左边界x坐标，上边界的y坐标，右边界的x坐标，下边界的y坐标
        # print('class: {}, score: {}'.format(CLASSES[cl], score))
        # print('box coordinate left,top,right,down: [{}, {}, {}, {}]'.format(top, left, right, bottom))
        if score < 0.8 :
            continue
        if CLASSES[cl] == target_name:
            center_x = (right-left)/2+left
            center_y = (bottom-top)/2+top
            target_list.update({index: [int(center_x), int(center_y)]})
            cv2.circle(image,(int(center_x),int(center_y)),5,(0,255,0),-1)
            index += 1
        cv2.rectangle(image, (left, top), (right, bottom), (255, 0, 0), 2)
        cv2.putText(image, '{0} {1:.2f}'.format(CLASSES[cl], score),
                    (left, top),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2)
    return image, target_list


'''
传入图片与检测目标
'''
def onnx_yolo(target_name,img_path='temp/item.jpg'):
    if target_name =="apple":
        target_name = "redapple"
    if target_name =="orange":
        target_name = "pear"
    print("开始识别")
    # 加载ONNX模型
    session = onnxruntime.InferenceSession('temp/best_s.onnx')
    img = cv2.imread(img_path)

    # 预处理图片（根据模型要求）
    or_img = cv2.resize(img, (640, 640))  # resize后的原图 (640, 640, 3)
    img = or_img[:, :, ::-1].transpose(2, 0, 1)  # BGR2RGB和HWC2CHW
    img = img.astype(dtype=np.float32)  # onnx模型的类型是type: float32[ , , , ]
    img /= 255.0
    img = np.expand_dims(img, axis=0)  # [3, 640, 640]扩展为[1, 3, 640, 640]

    # # 打印模型输入输出层名字
    # print(session.get_inputs()[0].name)
    # print(session.get_outputs()[0].name)

    # 第4步: 运行模型进行推断
    outputs = session.run(None, {session.get_inputs()[0].name: img})

    # 第5步: 处理模型输出
    predictions = outputs[0]

    # print(predictions.shape)
    outbox = filter_box(predictions, 0.25, 0.45)
    # #打印检测框
    # print('outbox( x1 y1 x2 y2 score class):')
    # print(outbox)
    if len(outbox) == 0:
        print('can not find object.')
    else:
        print('it is find object.')
        dest_img, target_list = draw(or_img, outbox,target_name)
        dest_img = cv2.resize(dest_img,(800,600))
        #创建多线程展示图像
        thread = threading.Thread(target=lambda: (
            
            cv2.imshow("result", dest_img),
            cv2.waitKey(0),
            cv2.destroyAllWindows()
        ))
        thread.start()
        if not target_list:
            return None
        center_point = random.choice(list(target_list.values()))
        center_point.append(1)
        return center_point

if __name__ == '__main__':
    target_list = onnx_yolo("redapple")
    print(target_list)