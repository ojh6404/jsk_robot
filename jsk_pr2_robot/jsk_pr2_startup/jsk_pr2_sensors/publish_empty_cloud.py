#!/usr/bin/env python

import rospy
from jsk_topic_tools import ConnectionBasedTransport
import math
from struct import *
from sensor_msgs.msg import PointCloud2, PointField


class PublishEmptyCloud(ConnectionBasedTransport):
    def __init__(self):
        super(PublishEmptyCloud, self).__init__()

        frame_id = rospy.get_param('~frame_id', 'base_laser_link')
        max_range = rospy.get_param('~max_range', 25.0)
        rotate_points = rospy.get_param('~rotate_points', False)

        self.pub_msg = self.make_empty_cloud(frame_id, max_range, rotate_points)

        self.rate = 1.0 / rospy.get_param('~rate', 10) ## Hz
        self.timer = None
        self.pub_cloud = self.advertise('empty_cloud', PointCloud2, queue_size=1)

    def subscribe(self):
        self.timer = rospy.Timer(rospy.Duration(self.rate), self.timer_callback)

    def unsubscribe(self):
        self.timer.stop()
        self.timer = None

    def make_empty_cloud(self, frame_id, max_range, rotate_points):
        irange = range(-314, 315)
        jrange = range(-314, 315)
        msg = PointCloud2()
        msg.header.frame_id = frame_id
        msg.height = 1
        if rotate_points:
            msg.width = len(irange) * len(jrange)
        else:
            msg.width = len(irange)

        msg_fieldx = PointField()
        msg_fieldy = PointField()
        msg_fieldz = PointField()
        msg_fieldx.name = 'x'
        msg_fieldx.offset = 0
        msg_fieldx.datatype = 7
        msg_fieldx.count = 1
        msg_fieldy.name = 'y'
        msg_fieldy.offset = 4
        msg_fieldy.datatype = 7
        msg_fieldy.count = 1
        msg_fieldz.name = 'z'
        msg_fieldz.offset = 8
        msg_fieldz.datatype = 7
        msg_fieldz.count = 1

        msg.fields = [msg_fieldx, msg_fieldy, msg_fieldz]
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width;
        msg.is_dense = True

        points = []
        for i in irange:
            x = max_range * math.cos(i*0.005)
            y = max_range * math.sin(i*0.005)
            if rotate_points:
                for j in jrange:
                    # x rotation
                    #            x = max_range * math.cos(i*0.005)
                    #            y = max_range * math.sin(i*0.005) * math.cos(j * 0.005)
                    #            z = -1 * max_range * math.sin(i*0.005) * math.sin(j * 0.005)
                    # y rotation
                    points.append(pack('<ffff', x * math.cos(j * 0.005), y, -1 * x * math.sin(j * 0.005), 0.0))
            else:
                points.append(pack('<ffff', x, y, 0.0, 0.0))

        msg.data = ''.join(points)
        return msg

    def timer_callback(self, event=None):
        self.pub_msg.header.stamp = rospy.Time.now()
        self.pub_cloud.publish(self.pub_msg)


if __name__ == '__main__':
    rospy.init_node("publish_empty_cloud")
    p = PublishEmptyCloud()
    rospy.spin()
