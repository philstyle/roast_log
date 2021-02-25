import cv2
import numpy
import time

DURATION = 300
FRAMES_PER_SECOND = 5
ROLLING_WINDOW_WIDTH = 1200
OUTPUT_HEIGHT = 400
OUTPUT_BUCKET_CAP = (OUTPUT_HEIGHT * 3) + 1

def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    framerate = cam.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)
    time.sleep(2)

    start_time = time.time()
    end_time = start_time + DURATION


    frame_time = (1.0 / FRAMES_PER_SECOND)

    frame_time_millis = int((frame_time * 1000))
    next_frame_time = start_time + frame_time


    number = 0

    while True:
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

	#see if we can show this
	if number > ROLLING_WINDOW_WIDTH:
	    startx = number - ROLLING_WINDOW_WIDTH
	    endx = number
	    partial_image = full_image[0:OUTPUT_HEIGHT, startx:endx]
	else:
	    partial_image = full_image

	cv2.imshow("Foo", partial_image)
        cv2.waitKey(1)

        if time.time() >= end_time:
	    filename = "./%s-%s-%sSec-%sFPS.png" % (start_time, end_time, DURATION, FRAMES_PER_SECOND)
            cv2.imwrite(filename, full_image)
            break

    #SHOW IS OVER
    #DO SOMETHING TO INDICATE WE ARE DONE RECORDING BUT ALSO JUST SHOW THE THING
    time.sleep(10)
    cv2.destroyAllWindows()


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()
