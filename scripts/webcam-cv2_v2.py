import cv2
import numpy
myimg = cv2.imread('image.jpg')


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(1)
    number = 0
    while True:
        ret_val, img = cam.read()
        #cv2.imwrite('testimage'+str(number)+'.png', img)

        avg_color_per_row = numpy.average(img, axis=0)
        avg_color = numpy.average(avg_color_per_row, axis=0)
        img = numpy.zeros((1,1,3), numpy.uint8)
        print(img)
        numpy.put(img, [0,1,2], avg_color)
        print(img)
        if number > 100000:
            padding="0"
        elif number >= 10000:
            padding="00" 
        elif number >= 1000:
            padding="000" 
        elif number >= 100:
            padding="0000" 
        elif number >= 10:
            padding="00000" 
        else:
            padding="000000"
        cv2.imwrite('testimage'+padding+str(number)+'.png', img)

        if mirror: 
            img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
        number += 1
    cv2.destroyAllWindows()


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()
