import cv2
import numpy
import time
from datetime import datetime

#Variables that adjust output
FRAMES_PER_SECOND = 5
MINOR_FRAMEMODULO = 30 * FRAMES_PER_SECOND
MAJOR_FRAMEMODULO = 60 * FRAMES_PER_SECOND
ROLLING_WINDOW_WIDTH = 1200
OUTPUT_HEIGHT = 400
OUTPUT_BUCKET_CAP = (OUTPUT_HEIGHT * 3) + 1
MARK_COLOR = 255


#VERSION 4

def show_webcam(cam):

    #cv2.namedWindow("roast", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("roast", ROLLING_WINDOW_WIDTH, OUTPUT_HEIGHT)

    time.sleep(2)
    #framerate = cam.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)
    #cam.set(3, 1600)
    #cam.set(4, 1200)

    start_time = time.time()

    frame_time = (1.0 / FRAMES_PER_SECOND)

    frame_time_millis = int((frame_time * 1000))
    next_frame_time = start_time + frame_time

    full_image = None
    
    number = 0

    while True:
      try:
        #waiting until at least next frame time
        now = time.time()
        if now < next_frame_time:
            time.sleep(next_frame_time - now)

        next_frame_time = start_time + ((number + 1) * frame_time)

        ret_val, orig_img = cam.read()
        if not ret_val:
            print("trouble connecting to %s" % (cam))
            break
        #cropped_img = orig_img[360:640, 720:1280]
	
	#for 1600x1200
        #cropped_img = orig_img[300:900, 400:1200]

        #for 1024x768
        #cropped_img = orig_img[192:576, 256:768]
        cropped_img = orig_img[288:480, 384:640]
        cv2.imshow("CROP", cropped_img)
        
        avg_color_per_row = numpy.average(cropped_img, axis=0)
        avg_color = numpy.average(avg_color_per_row, axis=0)
        img = numpy.zeros((OUTPUT_HEIGHT,1,3), numpy.uint8)

        first = 0
        second = 1
        third = 2

        while third < (OUTPUT_BUCKET_CAP - 12):
            numpy.put(img, [first,second,third], avg_color)
            first += 3
            second += 3
            third += 3
	#stopped four short, add 2 black pixels every major, 4 black pixels every minor

        if (number % MAJOR_FRAMEMODULO) == 0:
            while third < OUTPUT_BUCKET_CAP:
                numpy.put(img, [first,second,third], MARK_COLOR)
                first += 3
                second += 3
                third += 3
        elif (number % MINOR_FRAMEMODULO) == 0:
            while third < (OUTPUT_BUCKET_CAP - 6):
                numpy.put(img, [first,second,third], avg_color)
                first += 3
                second += 3
                third += 3
            numpy.put(img, [first,second,third], MARK_COLOR)
            first += 3
            second += 3
            third += 3
            numpy.put(img, [first,second,third], MARK_COLOR)
        else:
            while third < OUTPUT_BUCKET_CAP:
                numpy.put(img, [first,second,third], avg_color)
                first += 3
                second += 3
                third += 3



        if number == 0:
            full_image = img
        else:
            full_image = cv2.hconcat([full_image, img])

        number += 1

	#see if we can show this to the user
	#THIS CAN BE IMPROVED BY DEFINING THE SPACE AHEAD OF TIME I THINK

        if number > ROLLING_WINDOW_WIDTH:
            startx = number - ROLLING_WINDOW_WIDTH
            endx = number
            partial_image = full_image[0:OUTPUT_HEIGHT, startx:endx]
        else:
            partial_image = full_image

        cv2.imshow("roast", partial_image)
        cv2.waitKey(1)
      except KeyboardInterrupt:
        end_datetime = datetime.now().strftime("%Y.%m.%d.%H%M%S")
        end_time = time.time()
        DURATION = int(round(end_time - start_time))
        if DURATION > 60:
          mins = int(DURATION / 60)
          remain = DURATION % 60
          DURATION = str(mins) + "Min" + str(remain)
        filename = "./%s-%sSec-%sFPS.png" % (end_datetime, DURATION, FRAMES_PER_SECOND)
        cv2.imwrite(filename, full_image)
        break

    #SHOW IS OVER
    #DO SOMETHING TO INDICATE WE ARE DONE RECORDING BUT ALSO JUST SHOW THE THING
    #time.sleep(5)
    cv2.destroyAllWindows()


def main():
    show_webcam(cv2.VideoCapture(0))

if __name__ == '__main__':
    main()
