import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np

rospy.init_node('computer_vision_sample')
bridge = CvBridge()

blue_lower = np.array([100, 120, 80])
blue_upper = np.array([140, 255, 255])

image_pub = rospy.Publisher('~debug', Image, queue_size=1)

def image_callback(data):
    cv_image = bridge.imgmsg_to_cv2(data, 'bgr8')
    hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_image, blue_lower, blue_upper)

    image_pub.publish(bridge.cv2_to_imgmsg(cv_image, encoding="passthrough"))

image_sub = rospy.Subscriber('main_camera/image_raw', Image,
                             image_callback, queue_size=1)

rospy.spin()
