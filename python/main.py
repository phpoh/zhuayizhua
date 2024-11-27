import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont

# Mediapipe 初始化
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# 摄像头初始化
cap = cv2.VideoCapture(0)

# 触发条件：任意两个手指点重合（距离非常小）
def are_fingers_overlapping(hand_landmarks, threshold=0.01):
    # 获取手指尖的坐标
    points = [
        hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    ]
    
    # 计算任意两点之间的距离，判断是否小于阈值
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = np.linalg.norm(np.array([points[i].x, points[i].y]) - np.array([points[j].x, points[j].y]))
            if dist < threshold:  # 如果两点之间的距离小于阈值，则认为手指重合
                return True
    return False

# 模拟按下command + shift + 3（macOS 截图快捷键）
def simulate_screenshot():
    print("模拟按下 command + shift + 3 截屏")
    pyautogui.hotkey('command', 'shift', '3')  # 模拟 macOS 截图快捷键

# 在图像上绘制中文文本
def draw_chinese_text(image, text, position, font_size=30):
    # 转换为Pillow图像
    pil_img = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_img)
    
    # 使用系统字体
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", font_size)
    
    # 绘制文本
    draw.text(position, text, font=font, fill=(0, 255, 0))  # 绿色文字
    
    # 转回为OpenCV格式
    return np.array(pil_img)

# 主循环，摄像头检测
hand_overlap_detected_time = None  # 用于记录手指重合的时间
display_text_duration = 3  # 设置提示文字显示时间为3秒
screenshot_triggered = False  # 用于控制截图是否已经触发过

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 处理手势识别
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    # 创建一个黑色背景的画布
    output_frame = np.zeros_like(frame)

    # 如果检测到手
    hand_overlap_detected = False  # 标记手指重合状态

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制手部关键点和连接线
            mp_drawing.draw_landmarks(output_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 判断是否有两个手指重合
            if are_fingers_overlapping(hand_landmarks):
                hand_overlap_detected = True  # 如果手指重合，设置标志
                
                # 只有在截图未触发过的情况下才执行截图操作
                if not screenshot_triggered:
                    simulate_screenshot()  # 执行模拟截图
                    screenshot_triggered = True  # 设置截图已触发标志
                    hand_overlap_detected_time = time.time()  # 记录时间
                    time.sleep(1)  # 防止重复触发

    # 如果手指重合，添加提示文字
    if hand_overlap_detected:
        # 显示文本，设置显示时间
        if hand_overlap_detected_time and (time.time() - hand_overlap_detected_time) < display_text_duration:
            output_frame = draw_chinese_text(output_frame, "手指重合！触发截屏", (50, 50), font_size=30)

    # 如果手指不再重合，允许下一次触发截图
    # if not hand_overlap_detected:
    #     screenshot_triggered = False

    # 显示手部图像
    cv2.imshow('Hand Gesture Detection', output_frame)
    
    
    # 按'q'键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
