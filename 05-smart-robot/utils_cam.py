import cv2
from cv2 import imshow
import os

def open_camera_video():
    '''
    摄像头模块
    :return:
    result:是否成功启动摄像头
    '''
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("摄像头打开失败")
        return
    while True:
        ret,frame = cap.read()
        if not ret:
            "帧读取失败"
            break
        imshow("frame", frame)
        if  cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def top_view_shot(save_path='temp/item.jpg'):
    # 确保temp目录存在
    os.makedirs('temp', exist_ok=True)

    # 打开摄像头（默认第一个摄像头）
    cap = cv2.VideoCapture(0)

    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        return False

        # 读取一帧图像
    ret, frame = cap.read()

    if ret:
        # 保存图像
        cv2.imwrite(save_path, frame)
        print(f"图片已保存到 {save_path}")

        # 释放摄像头资源
        cap.release()
        return True
    else:
        print("捕获图像失败")
        cap.release()
        return False
        
if __name__ == '__main__':

    ret = top_view_shot()
    print(ret)