import os
import pytesser
from PIL import Image,ImageEnhance

cwd = os.getcwd()
os.chdir("D:\\Anaconda2\\Lib\\site-packages\\pytesser")

# im=Image.open("E:\\trader_work\\tools\\verification\\veriCode.jpg")
# imgry = im.convert('L')
# sharpness =ImageEnhance.Contrast(imgry)
# sharp_img = sharpness.enhance(2.0)
# sharp_img.save("E:\\trader_work\\tools\\verification\\veriCode1.jpg")

def sum_9_region(pix, width, height, x, y):
    cur_pixel = pix[x, y]

    if cur_pixel == 1:
        return 0

    sum = 0
    if y == 0:
        if x == 0:
            sum = cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x + 1, y] \
                  + pix[x + 1, y + 1]
            sum = 4 - sum
        elif x == width - 1:
            sum = cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x - 1, y] \
                  + pix[x - 1, y + 1]
            sum = 4 - sum
        else:
            sum = pix[x - 1, y] \
                  + pix[x - 1, y + 1] \
                  + cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x + 1, y] \
                  + pix[x + 1, y + 1]
            sum = 6 - sum
    elif y == height - 1:
        if x == 0:
            sum = cur_pixel \
                  + pix[x + 1, y] \
                  + pix[x + 1, y - 1] \
                  + pix[x, y - 1]
            sum = 4 - sum
        elif x == width - 1:
            sum = cur_pixel \
                  + pix[x, y - 1] \
                  + pix[x - 1, y] \
                  + pix[x - 1, y - 1]
            sum = 4 - sum
        else:
            sum = cur_pixel \
                  + pix[x - 1, y] \
                  + pix[x + 1, y] \
                  + pix[x, y - 1] \
                  + pix[x - 1, y - 1] \
                  + pix[x + 1, y - 1]
            sum = 6 - sum
    else:
        if x == 0:
            sum = pix[x, y - 1] \
                  + cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x + 1, y - 1] \
                  + pix[x + 1, y] \
                  + pix[x + 1, y + 1]
            sum = 6 - sum
        elif x == width - 1:
            sum = pix[x, y - 1] \
                  + cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x - 1, y - 1] \
                  + pix[x - 1, y] \
                  + pix[x - 1, y + 1]
            sum = 6 - sum
        else:
            sum = pix[x - 1, y - 1] \
                  + pix[x - 1, y] \
                  + pix[x - 1, y + 1] \
                  + pix[x, y - 1] \
                  + cur_pixel \
                  + pix[x, y + 1] \
                  + pix[x + 1, y - 1] \
                  + pix[x + 1, y] \
                  + pix[x + 1, y + 1]
            sum = 9 - sum
    return sum

def pIx(pix, width, height):
    for x in xrange(1,width-1):
        if x > 1 and x != width-2:
            left = x - 1
            right = x + 1

        for y in xrange(1,height-1):
            up = y - 1
            down = y + 1

            if x <= 2 or x >= (width - 2):
                pix[x,y] = 1

            elif y <= 2 or y >= (height - 2):
                pix[x,y] = 1

            elif pix[x,y] == 0:
                if y > 1 and y != height-1:
                    up_color = pix[x,up]
                    down_color = pix[x,down]
                    left_color = pix[left,y]
                    left_down_color = pix[left,down]
                    right_color = pix[right,y]
                    right_up_color = pix[right,up]
                    right_down_color = pix[right,down]
                    
                    if down_color == 0:
                        if left_color == 1 and left_down_color == 1 and right_color == 1 and right_down_color == 1:
                            pix[x,y] = 1
                            
                    elif right_color == 0:
                        if down_color == 1 and right_down_color == 1 and up_color == 1 and right_up_color == 1:
                            pix[x,y] = 1

                if left_color == 1 and right_color == 1 and up_color == 1 and down_color == 1:
                    pix[x,y] = 1

def clear_noise(pix, width, height):
    for y in xrange(1,height-1):
        for x in xrange(1, width-1):
            p = []
            p.append(pix[x-1, y-1])
            p.append(pix[x, y - 1])
            p.append(pix[x + 1, y - 1])
            p.append(pix[x - 1, y])
            p.append(pix[x, y])
            p.append(pix[x + 1, y])
            p.append(pix[x - 1, y + 1])
            p.append(pix[x, y + 1])
            p.append(pix[x + 1, y + 1])

            for j in xrange(0,5):
            	for i in xrange(j+1,9):
	                if p[j] > p[i]:
	                    s = p[j]
	                    p[j] = p[i]
	                    p[i] = s

	        pix[x, y] = p[4]

  
threshold = 200
table = []
for i in range(256):
    if i < threshold:
        table.append(1)
    else:
        table.append(0)

im = Image.open("E:\\trader_work\\tools\\verification\\F9126F7312A04DE397B2AE2CE20E648E.jpg")
imgry = im.convert('L')
out = imgry.point(table,'1')
pix = out.load()
width, height = out.size
clear_noise(pix, width, height)
# for x in xrange(0,width):
# 	for y in xrange(0,height):
# 		sum = sum_9_region(pix, width, height, x, y)
# 		if sum <= 2:
# 			pix[x, y] = 1
out.save("E:\\trader_work\\tools\\verification\\F9126F7312A04DE397B2AE2CE20E648E1.jpg")

print pytesser.image_to_string(out)