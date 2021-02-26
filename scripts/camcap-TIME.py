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

def show_webcam(camera):
    cam = camera
    framerate = cam.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)
    time.sleep(2)
    

    #HAD TO PUT THIS HERE I DONT KNOW WHY
    DURATION = 71


    start_time = time.time()
    end_time = start_time + DURATION

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
            print("trouble!")
            continue
        cropped_img = orig_img[360:640, 720:1280]

        #cv2.imwrite('testimage'+str(number)+'.png', cropped_img)

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

	cv2.imshow("Foo", partial_image)
        cv2.waitKey(1)
	if time.time() >= end_time:
	    if DURATION > 60:
              mins = DURATION / 60
              remain = DURATION % 60
              DURATION = str(mins) + "Min" + str(remain)
	    end_datetime = datetime.now().strftime("%Y.%m.%d.%H%M%S")
            filename = "./%s-%sSec-%sFPS.png" % (end_datetime, DURATION, FRAMES_PER_SECOND)
            cv2.imwrite(filename, full_image)
            break
      except KeyboardInterrupt:
	end_datetime = datetime.now().strftime("%Y.%m.%d.%H%M%S")
	end_time = time.time()
	DURATION = int(round(end_time - start_time))
	if DURATION > 60:
          mins = DURATION / 60
          remain = DURATION % 60
          DURATION = str(mins) + "Min" + str(remain)
	filename = "./%s-%sSec-%sFPS.png" % (end_datetime, DURATION, FRAMES_PER_SECOND)
        cv2.imwrite(filename, full_image)
        break

    #SHOW IS OVER
    #DO SOMETHING TO INDICATE WE ARE DONE RECORDING BUT ALSO JUST SHOW THE THING
    time.sleep(5)
    cv2.destroyAllWindows()


def main():
    show_webcam(cv2.VideoCapture(0))

if __name__ == '__main__':
    main()
