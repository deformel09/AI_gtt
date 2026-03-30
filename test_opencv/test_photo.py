import cv2
import numpy as np
import cv2.aruco as aruco

lower_blue = np.array([90, 90, 0])
upper_blue = np.array([150, 255, 255])

img = cv2.imread('test.jpg')

if img is None:
    print("Ошибка загрузки test.jpg")
    exit()

img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
# Исправьте срез: ширина 200 пикселей
img_roi = img[200:550, 100:400]  # Теперь (200, 200, 3)
print("ROI shape:", img_roi.shape)


def skeleton(img):
    x1 = (img.shape[1] // 2) - 250
    y1 = (img.shape[0] // 2) - 250
    x2 = (img.shape[1] // 2) + 250
    y2 = (img.shape[0] // 2) + 250

    # Гарантируем 3 канала
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv_img, lower_blue, upper_blue)

    # Thinning на бинарной маске (1 канал)
    skel = cv2.ximgproc.thinning(blue_mask, cv2.ximgproc.THINNING_ZHANGSUEN)

    ys, xs = np.where(skel > 0)
    points = list(zip(xs, ys))

    endpoints = []
    for x, y in points:
        x0, x1 = max(x - 1, 0), min(x + 2, skel.shape[1])
        y0, y1 = max(y - 1, 0), min(y + 2, skel.shape[0])
        roi = skel[y0:y1, x0:x1]
        if 1 <= cv2.countNonZero(roi) <= 2:
            endpoints.append((x, y))

    # print(f"Endpoints: {endpoints}")  # Для отладки
    return skel

def aruco_detect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None or len(corners) == 0:
        print("Метки не найдены")
        return None

    h, w = gray.shape[:2]
    img_center = np.array([w / 2, h / 2], dtype=np.float32)

    best_idx = None
    best_dist = None

    for i, marker in enumerate(corners):
        pts = marker.reshape(4, 2)
        center = pts.mean(axis=0)
        dist = np.linalg.norm(center - img_center)

        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_idx = i

    central_corners = corners[best_idx].reshape(4, 2)
    central_id = int(ids[best_idx][0])

    print(f"Центральная метка: ID = {central_id}")
    print("Ее углы:")
    print(central_corners)

    aruco.drawDetectedMarkers(image, [corners[best_idx]], ids[best_idx:best_idx+1])

    return central_corners


def detect(skel, corner_aruco):
    corners = corner_aruco[0].reshape(-1, 2)  # превращаем в (N, 2)
    x_min = int(corners[:, 0].min())
    x_max = int(corners[:, 0].max())
    y_min = int(corners[:, 1].min())
    y_max = int(corners[:, 1].max())
    points = 0

    skel_up = skel[y_min - 100 :y_min, x_min:x_max]
    skel_down = skel[y_max:y_max + 100, x_min:x_max]
    skel_left = skel[y_min:y_max, x_min - 100:x_min]
    skel_right = skel[y_min:y_max, x_max:x_max + 100]

    white_coords_up = np.where(skel_up > 0)
    n_white_up = len(white_coords_up[0])

    white_coords_down = np.where(skel_down > 0)
    n_white_down = len(white_coords_down[0])

    white_coords_left = np.where(skel_left > 0)
    n_white_left = len(white_coords_left[0])

    white_coords_right = np.where(skel_right > 0)
    n_white_right = len(white_coords_right[0])

    if n_white_right > 5:
        points += 1
    if n_white_left > 5:
        points += 1
    if n_white_up > 5:
        points += 1
    if n_white_down > 5:
        points += 1

    return points

def main(points, img, corner_aruco):
    corners = corner_aruco[0].reshape(-1, 2)  # превращаем в (N, 2)
    x_min = int(corners[:, 0].min())
    x_max = int(corners[:, 0].max())
    y_min = int(corners[:, 1].min())
    y_max = int(corners[:, 1].max())
    final = img
    if points == 3:
        final = cv2.rectangle(img, (x_min - 100,y_min - 100), (x_max + 100,y_max + 100), (255, 0, 0), 2)
        final = cv2.putText(final, 'free', (x_min - 105, y_min - 105), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return final
# Используйте ROI
cv2.imshow('mask', skeleton(img_roi))
cv2.imshow('final', main(detect(skeleton(img_roi), aruco_detect(img_roi)), img_roi, aruco_detect(img_roi)))
# cv2.imshow('mask ROI', detect(skeleton(img_roi), aruco_detect(img_roi)))
# cv2.imshow('aruco', aruco_detect(img_roi))
detect(skeleton(img_roi), aruco_detect(img_roi))
cv2.waitKey(0)
cv2.destroyAllWindows()