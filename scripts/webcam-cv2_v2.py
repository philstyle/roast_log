import cv2
import numpy
myimg = cv2.imread('image.jpg')


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    number = 0
    while True:
        ret_val, img = cam.read()
        #cv2.imwrite('testimage'+str(number)+'.png', img)

        avg_color_per_row = numpy.average(img, axis=0)
        avg_color = numpy.average(avg_color_per_row, axis=0)
        img = numpy.zeros((1000,1,3), numpy.uint8)
        #print(img)
        first = 0
        second = 1
        third = 2
        while third < 3001:
            numpy.put(img, [first,second,third], avg_color)
            first += 3
            second += 3
            third += 3
        #print(img)
        if number > 10000000:
            padding="0"
        elif number >= 1000000:
            padding="00" 
        elif number >= 100000:
            padding="000" 
        elif number >= 10000:
            padding="0000" 
        elif number >= 1000:
            padding="00000" 
        elif number >= 100:
            padding="000000" 
        elif number >= 10:
            padding="0000000" 
        else:
            padding="00000000"
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
