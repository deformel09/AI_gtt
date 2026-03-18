import rospy
from clover import srv
from std_srvs.srv import Trigger
rospy.init_node('flight')

navigate = rospy.ServiceProxy('navigate', srv.Navigate)
land = rospy.ServiceProxy('land', Trigger)
set_effect = rospy.ServiceProxy('led/set_effect', SetLEDEffect)

navigate(x=0, y=0, z=1.5, speed=0.5, frame_id='body', auto_arm=True)
rospy.sleep(5)
set_effect(r=0, g=255, b=0)
land()
































