import cv2
import numpy
import time
import picamera
import picamera.array
from datetime import datetime

# Variables that adjust output
FRAMES_PER_SECOND = 5
MINOR_FRAMEMODULO = 30 * FRAMES_PER_SECOND
MAJOR_FRAMEMODULO = 60 * FRAMES_PER_SECOND
ROLLING_WINDOW_WIDTH = 1000
OUTPUT_HEIGHT = 400
OUTPUT_BUCKET_CAP = (OUTPUT_HEIGHT * 3) + 1
MARK_COLOR = 0
PICAM_CLASS= "<class 'picamera.camera.PiCamera'>"

RESOLUTION = (320,320)
FRAMERATE = FRAMES_PER_SECOND * 2
CAM_ISO = 400
CAM_EXPO = 'off'
CAM_SHUT = 0
CAM_EXPO_SP = 0
CAM_AWB_MODE = 'off'
CAM_AWB_GAINS = 0
IMAGE_TYPE='bgr'

# VERSION 9
# 1 second buffer until the average color changes "significantly" for more than 3 frames
BUFFER = [[0.0,0.0,0.0]] * (FRAMES_PER_SECOND * 2)

STOP_FRAME = [0.0,0.0,0.0]

def print_buffer():
    for i in range(FRAMES_PER_SECOND):
        #print("BUFFER %i: %f" % (i, BUFFER[i]))
        print(BUFFER[i])

def spool(camera):
    start_time = time.time()
    frame_time = (1.0 / FRAMES_PER_SECOND)
    next_frame_time = start_time + frame_time
    #fill up the buffer with frames, then start evaluating new frames against the oldest
    #if newest 3 frames are all "significantly different" stop spooling (assume something will start recording)
    #BASED ON A BIT OF TESTING
    #a diff greater than 50 for 3 frames is sufficient
    frame = 0
    hits = 0
    while True:
        # waiting until at least next frame time
        now = time.time()
        if now < next_frame_time:
            time.sleep(next_frame_time - now)
        next_frame_time = start_time + ((frame + 1) * frame_time)
        #now it is definitely time for the next frame
        image = numpy.empty((320,320,3), dtype=numpy.uint8)
        camera.capture(image, IMAGE_TYPE, True)
        image = image[:320, :320]
        #cropped_img = orig_img[288:480, 384:640]
        cropped_img = image
        avg_color_per_row = numpy.average(cropped_img, axis=0)
        avg_color = numpy.average(avg_color_per_row, axis=0)
        if frame < (FRAMES_PER_SECOND * 3):
            BUFFER[frame % (FRAMES_PER_SECOND * 2)] = avg_color
        else:
            if frame == (FRAMES_PER_SECOND * 3):
                global STOP_FRAME
                STOP_FRAME = avg_color
                #STORING STOP FRAME FOR CATCHING END OF ROAST
            print(avg_color)
            #TIME TO COMPARE
            #THIS FRAME TO FRAME #FRAMES_PER_SECOND ago?
            check_1 = numpy.linalg.norm(avg_color - BUFFER[(frame + 1) % FRAMES_PER_SECOND] )
            check_2 = numpy.linalg.norm(avg_color - BUFFER[(frame + 2) % FRAMES_PER_SECOND] )
            check_3 = numpy.linalg.norm(avg_color - BUFFER[(frame + 3) % FRAMES_PER_SECOND] )
            sumdiff = check_1 + check_2 + check_3
            if sumdiff < 50:
                hits = 0
            if sumdiff > 80:
                hits += 1
            if hits >= 3:
                #sufficient
                break
            print(sumdiff)
            #print_buffer()
            BUFFER[frame % (FRAMES_PER_SECOND * 2)] = avg_color
            #break
        #increment frame
        frame += 1

def distance_from_end(avg_color):
    #return euclidean distance between average color and stop frame color
    #print (STOP_FRAME)
    return numpy.linalg.norm(avg_color - STOP_FRAME )

def build_image(number, average_color, image_being_built):
    img = numpy.zeros((OUTPUT_HEIGHT, 1, 3), numpy.uint8)

    first = 0
    second = 1
    third = 2
    # normally just put the average color into the array
    while third < (OUTPUT_BUCKET_CAP - 12):
        numpy.put(img, [first, second, third], average_color)
        first += 3
        second += 3
        third += 3
    # stopped four short, add 2 pixels every major, 4 pixels every minor
    if (number % MAJOR_FRAMEMODULO) == 0:
        while third < (OUTPUT_BUCKET_CAP - 3):
            numpy.put(img, [first, second, third], MARK_COLOR)
            first += 3
            second += 3
            third += 3
        numpy.put(img, [first, second, third], MARK_COLOR)
    elif (number % MINOR_FRAMEMODULO) == 0:
        while third < (OUTPUT_BUCKET_CAP - 12):
            numpy.put(img, [first, second, third], average_color)
            first += 3
            second += 3
            third += 3
        numpy.put(img, [first, second, third], MARK_COLOR)
        first += 3
        second += 3
        third += 3
        numpy.put(img, [first, second, third], MARK_COLOR)
    else:
        while third < OUTPUT_BUCKET_CAP:
            numpy.put(img, [first, second, third], average_color)
            first += 3
            second += 3
            third += 3

    if image_being_built is None:
        image_being_built = img
    else:
        image_being_built = cv2.hconcat([image_being_built, img])

    return image_being_built

def get_image_from(camera):
    camclass = str(type(camera))
    if camclass == PICAM_CLASS:
      print("PICAM CLASS!")
    else:
      print(PICAM_CLASS)
      print(type(camera))
    return cropped_image

def record_webcam(camera):
    start_time = time.time()
    frame_time = (1.0 / FRAMES_PER_SECOND)
    next_frame_time = start_time + frame_time

    # setup_image for prep before to get lined up and greycard
    setup_image = None

    # full_image for final roast output image
    full_image = None
    number = 0
    endframes = 0
    #if we get to 5 endframes, shut it down (endframes mean distance from STOP_FRAME of less tahn ??
    while True:
        try:
            # waiting until at least next frame time
            now = time.time()
            if now < next_frame_time:
                print("waiting %s" % ((next_frame_time - now)))
                time.sleep(next_frame_time - now)
            
            next_frame_time = start_time + ((number + 1) * frame_time)
            image = numpy.empty((320,320,3), dtype=numpy.uint8)
            camera.capture(image, IMAGE_TYPE, True)
            image = image[:320, :320]
            # cropped_img = orig_img[360:640, 720:1280]

            # for 1600x1200
            # cropped_img = orig_img[300:900, 400:1200]

            # for 1024x768
            # cropped_img = orig_img[192:576, 256:768]
            #cropped_img = orig_img[288:480, 384:640]
            cropped_img = image
            #cv2.imshow("CROP", cropped_img)

            avg_color_per_row = numpy.average(cropped_img, axis=0)
            avg_color = numpy.average(avg_color_per_row, axis=0)

            full_image = build_image(number, avg_color, full_image)

            number += 1

            # see if we can show this to the user
            # THIS CAN BE IMPROVED BY DEFINING THE SPACE AHEAD OF TIME I THINK

            if number > ROLLING_WINDOW_WIDTH:
                startx = number - ROLLING_WINDOW_WIDTH
                endx = number
                partial_image = full_image[0:OUTPUT_HEIGHT, startx:endx]
            else:
                partial_image = full_image

            #cv2.imshow("roast", partial_image)
            #cv2.waitKey(1)
            #####print(avg_color)
            #####print(distance_from_end(avg_color))
            if distance_from_end(avg_color) < 10:
                #increment counter for end tracking
                endframes += 1
            else:
                endframes = 0
            if endframes >= 5:
                end_datetime = datetime.now().strftime("%Y.%m.%d.%H%M%S")
                end_time = time.time()
                duration = int(round(end_time - start_time))
                if duration > 60:
                    mins = int(duration / 60)
                    remain = duration % 60
                    duration = str(mins) + "Min" + str(remain)
                filename = "./%s-%sSec-%sFPS%s.png" % (end_datetime, duration, FRAMES_PER_SECOND, number)
                cv2.imwrite(filename, full_image)
                break
        except KeyboardInterrupt:
            end_datetime = datetime.now().strftime("%Y.%m.%d.%H%M%S")
            end_time = time.time()
            duration = int(round(end_time - start_time))
            if duration > 60:
                mins = int(duration / 60)
                remain = duration % 60
                duration = str(mins) + "Min" + str(remain)
            filename = "./%s-%sSec-%sFPS%s.png" % (end_datetime, duration, FRAMES_PER_SECOND, number)
            cv2.imwrite(filename, full_image)
            break

    # SHOW IS OVER
    # DO SOMETHING TO INDICATE WE ARE DONE RECORDING BUT ALSO JUST SHOW THE THING
    # time.sleep(5)
    cv2.destroyAllWindows()
    camera.close()
###
### MUST STILL FIND A WAY TO DEAL WITH WHITEBALANCE AND COLOR CONTROL
###
def set_camera_settings(camera):
    camera.set(cv2.CAP_PROP_AUTO_WB, 0.0)
    camera.set(cv2.CAP_PROP_WB_TEMPERATURE, 5500.0)
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    camera.set(cv2.CAP_PROP_EXPOSURE, 60.0)

###
### SHOULD SUGGEST ENDING POINT WITH TIME AND IMAGE BUT KEEP BUFFERING IF NO (then dump buffer into image and keep going)?
###
def main():
    #camera = cv2.VideoCapture(0)
    with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        camera.iso = CAM_ISO
        time.sleep(3)
        #print("shutter speed")
        #print(camera.shutter_speed)
        #print("exposure_speed")
        #print(camera.exposure_speed)
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        #camera.shutter_speed = 20000
        #print(camera.shutter_speed)
        print(g)
        camera.zoom=[0.5,0.5,0.25,0.25]
        #camera.start_preview()

        spool(camera)
        record_webcam(camera)

if __name__ == '__main__':
    main()
