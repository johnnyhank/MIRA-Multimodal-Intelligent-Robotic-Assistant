import cv2
import numpy as np

# 鼠标回调函数
def mouse_callback(event, x, y, flags, param):
    # 鼠标左键点击事件
    if event == cv2.EVENT_LBUTTONDOWN:
        # 打印坐标
        print(f"[{x}, {y}],")

# 创建窗口
cv2.namedWindow('Image')
# 设置鼠标回调
cv2.setMouseCallback('Image', mouse_callback)

# 打开默认摄像头（通常是0或1）
cap = cv2.VideoCapture(0)

# 设置摄像头分辨率（可选）
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 显示图像
while True:
    # 读取一帧
    ret, frame = cap.read()
    
    # 检查是否成功读取帧
    if not ret:
        print("无法获取帧")
        break
    
    # 调整图像大小（可选）
    or_img = cv2.resize(frame, (640, 640))
    
    cv2.imshow('Image', or_img)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()