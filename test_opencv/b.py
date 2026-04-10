import cv2
import numpy as np
import cv2.aruco as aruco
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from clover import long_callback

lower_blue = np.array([90, 90, 0])
upper_blue = np.array([150, 255, 255])
TARGET_ID = None
ROI_MARGIN = 200


def aruco_detect(image, target_id=None):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is None or len(corners) == 0:
        print("Метки не найдены")
        return None

    best_idx = None
    if target_id is not None:
        ids_flat = ids.flatten()
        found = np.where(ids_flat == target_id)[0]
        if len(found) == 0:
            print(f"Метка ID={target_id} не найдена")
            return None
        best_idx = int(found[0])
    else:
        h, w = gray.shape[:2]
        img_center = np.array([w / 2.0, h / 2.0], dtype=np.float32)
        best_dist = None
        for i, marker in enumerate(corners):
            pts = marker.reshape(4, 2)
            center = pts.mean(axis=0)
            dist = np.linalg.norm(center - img_center)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_idx = i

    return corners[best_idx].reshape(4, 2)


def skeleton_near_aruco(image, corner_aruco, margin=200):
    # Проверяем, что corner_aruco не None
    if corner_aruco is None:
        return None, None

    x_min = int(corner_aruco[:, 0].min())
    x_max = int(corner_aruco[:, 0].max())
    y_min = int(corner_aruco[:, 1].min())
    y_max = int(corner_aruco[:, 1].max())

    x1 = max(0, x_min - margin)
    y1 = max(0, y_min - margin)
    x2 = min(image.shape[1], x_max + margin)
    y2 = min(image.shape[0], y_max + margin)

    roi = image[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    skel = cv2.ximgproc.thinning(blue_mask, cv2.ximgproc.THINNING_ZHANGSUEN)

    return skel, (x1, y1)


def detect(skel, corner_aruco, roi_offset):
    if corner_aruco is None or skel is None:
        return None

    roi_x, roi_y = roi_offset
    local_corners = corner_aruco.copy()
    local_corners[:, 0] -= roi_x
    local_corners[:, 1] -= roi_y

    x_min = int(local_corners[:, 0].min())
    x_max = int(local_corners[:, 0].max())
    y_min = int(local_corners[:, 1].min())
    y_max = int(local_corners[:, 1].max())

    h, w = skel.shape[:2]

    def crop(x1, y1, x2, y2):
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        if x1 >= x2 or y1 >= y2:
            return np.zeros((0, 0), dtype=np.uint8)
        return skel[y1:y2, x1:x2]

    skel_up = crop(x_min, y_min - 100, x_max, y_min)
    skel_down = crop(x_min, y_max, x_max, y_max + 100)
    skel_left = crop(x_min - 100, y_min, x_min, y_max)
    skel_right = crop(x_max, y_min, x_max + 100, y_max)

    points = 0
    if cv2.countNonZero(skel_right) > 20:
        points += 1
    if cv2.countNonZero(skel_left) > 20:
        points += 1
    if cv2.countNonZero(skel_up) > 5:
        points += 1
    if cv2.countNonZero(skel_down) > 5:
        points += 1

    return points


def draw_result(image, corner_aruco, points):
    result = image.copy()
    if corner_aruco is None:
        return result

    aruco.drawDetectedMarkers(result, [corner_aruco.reshape(1, 4, 2).astype(np.float32)])

    x_min = int(corner_aruco[:, 0].min())
    x_max = int(corner_aruco[:, 0].max())
    y_min = int(corner_aruco[:, 1].min())
    y_max = int(corner_aruco[:, 1].max())

    if points == 3:
        cv2.rectangle(result, (x_min - 100, y_min - 100), (x_max + 100, y_max + 100), (255, 0, 0), 2)
        cv2.putText(result, 'free', (x_min - 105, y_min - 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return result


rospy.init_node('detect_parking')
bridge = CvBridge()


@long_callback
def image_callback(data):
    img = bridge.imgmsg_to_cv2(data, 'bgr8')  # OpenCV image
    img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))

    corner_aruco = aruco_detect(img, TARGET_ID)

    # Проверяем, что метка найдена, прежде чем продолжить
    if corner_aruco is not None:
        skel, roi_offset = skeleton_near_aruco(img, corner_aruco, ROI_MARGIN)
        points = detect(skel, corner_aruco, roi_offset)
        final = draw_result(img, corner_aruco, points)
    else:
        # Если метка не найдена, просто отображаем исходное изображение
        final = img

    image_pub.publish(bridge.cv2_to_imgmsg(final, 'bgr8'))


image_sub = rospy.Subscriber('main_camera/image_raw', Image, image_callback)
image_pub = rospy.Publisher('~debug', Image, queue_size=1)  # Исправлено предупреждение
rospy.spin()