import sensor, image, time

from pid import PID
from pyb import Servo

pan_servo=Servo(1)
tilt_servo=Servo(2)

pan_servo.calibration(500,2500,500)
tilt_servo.calibration(500,2500,500)

red_threshold  = (13, 49, 18, 61, 6, 47)

pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
#tilt_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_contrast(3)
sensor.set_gainceiling(16)
sensor.set_pixformat(sensor.GRAYSCALE) # use RGB565.
sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
sensor.set_vflip(True)
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.
face_cascade = image.HaarCascade("frontalface", stages=25)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    faces = img.find_features(face_cascade, threshold=0.75, scale=1.25)
    if faces:
        face = find_max(faces)
        cx = int(face[0]+face[2]/2)
        cy = int(face[1]+face[3]/2)
        pan_error = cx-img.width()/2
        tilt_error = cy-img.height()/2

        print("pan_error: ", pan_error)

        img.draw_rectangle(face) # rect
        img.draw_cross(cx, cy) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)
        tilt_output=tilt_pid.get_pid(tilt_error,1)
        print("pan_output",pan_output)
        pan_servo.angle(int(pan_servo.angle()+pan_output))
        tilt_servo.angle(int(tilt_servo.angle()+tilt_output))
