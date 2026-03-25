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

    # print("corners:", corners)
    # print("ids:", ids)
    # print("rejected:", rejected)

    if ids is not None and len(ids) > 0:
        print(f"Найдены маркеры: IDs = {ids.flatten()}")
        aruco.drawDetectedMarkers(image, corners, ids)
    else:
        print("Метки не найдены")
    print(corners)
    return corners  # Верните image!


def detect(skel, corner_aruco):
    if isinstance(corner_aruco, tuple):
        corner_aruco = corner_aruco[0]

    skel_1 = skel[int(corner_aruco[0, 1, 1]):int(corner_aruco[1, 1, 1]),
             int(corner_aruco[0, 0, 0]):int(corner_aruco[0, 0, 0]) + 50]
    # остальной код...

    white_coords_1 = np.where(skel_1 > 0)
    n_white_1 = len(white_coords_1[0])
    if n_white_1 > 4:
        print("FINE")



# Используйте ROI
cv2.imshow('mask', skeleton(img_roi))
# cv2.imshow('aruco', aruco_detect(img_roi))
detect(skeleton(img_roi), aruco_detect(img_roi))
cv2.waitKey(0)
cv2.destroyAllWindows()