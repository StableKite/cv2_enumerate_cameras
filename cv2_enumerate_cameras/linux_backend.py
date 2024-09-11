from cv2_enumerate_cameras.camera_info import CameraInfo
import os
from linuxpy.video.device import iter_video_capture_devices

try:
    import cv2
    CAP_GSTREAMER = cv2.CAP_GSTREAMER
    CAP_V4L2 = cv2.CAP_V4L2
except ModuleNotFoundError:
    CAP_GSTREAMER = 1800
    CAP_V4L2 = 200

supported_backends = (CAP_GSTREAMER, CAP_V4L2)


def read_line(*args):
    try:
        with open(os.path.join(*args)) as f:
            line = f.readline().strip()
        return line
    except IOError:
        return None


def cameras_generator(apiPreference):
    for device in iter_video_capture_devices():
        path = device.PREFIX + str(device.index)
        index = device.index
        # find device name and index
        device_name = os.path.basename(path)
        if not device_name[5:].isdigit():
            continue
        index = int(device_name[5:])

        # read camera name
        video_device_path = f'/sys/class/video4linux/{device_name}'
        video_device_name_path = os.path.join(video_device_path, 'name')
        if os.path.exists(video_device_name_path):
            name = read_line(video_device_name_path)
        else:
            name = device_name

        # find vendor id and product id
        vid = None
        pid = None
        usb_device_path = os.path.join(video_device_path, 'device')
        if os.path.exists(usb_device_path):
            usb_device_path = os.path.realpath(usb_device_path)

            if ':' in os.path.basename(usb_device_path):
                usb_device_path = os.path.dirname(usb_device_path)

            vid = int(read_line(usb_device_path, 'idVendor'), 16)
            pid = int(read_line(usb_device_path, 'idProduct'), 16)

        yield CameraInfo(index, name, path, vid, pid, apiPreference)


__all__ = ['supported_backends', 'cameras_generator']
