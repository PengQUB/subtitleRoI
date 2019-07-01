import cv2
import pytesseract
import numpy as np

if __name__ == '__main__':
    img = cv2.imread('news2.jpg')
    vis = img.copy()  # 用于绘制矩形框图
    orig = img.copy()  # 用于绘制不重叠的矩形框图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    cv2.imshow('binary', binary)

    # 膨胀、腐蚀
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 9))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 6))  # (24, 6)

    # 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations=1)
    cv2.imshow('dilation1', dilation)

    # 腐蚀一次，去掉细节
    erosion = cv2.erode(dilation, element1, iterations=1)
    cv2.imshow('erosion', erosion)

    # 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations=2)
    cv2.imshow('dilation2', dilation2)

    # 查找轮廓和筛选文字区域
    region = [ ]
    _, contours, hierarchy = cv2.findContours(dilation2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        cnt = contours[i]
        # 计算轮廓面积，并筛选掉面积小的
        area = cv2.contourArea(cnt)
        if (area < 1000):
            continue

        # 找到最小外接矩形
        rect = cv2.minAreaRect(cnt)  # 返回最小外接矩形(中心(x,y), (宽，高), 旋转角度)
        print("rect is: ")
        print(rect)

        # box是四个点的坐标
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        print(box)

        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])

        # 根据文字特征，筛选那些太细的矩形，留下扁的
        if (height > width * 1.3):
            continue

        # filter half screen
        minh = 600
        for h in box[:, 1]:
            if h < minh:
                minh = h

        if minh < 600:
            continue

        minw = 300
        maxw = 1000
        for w in box[:, 0]:
            if w < minw:
                minw = w
            if w > maxw:
                maxw = w

        if minw < 300 or maxw > 1000:
            continue

        region.append(box)


    # 绘制轮廓
    # for box in region:
    #     cv2.drawContours(img, [box], 0, (0, 0, 255), 2)

    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite("./box2.jpg", img)
    for i, box in enumerate(region):
        listx = []
        listy = []
        listx = box[:, 0]
        listy = box[:, 1]
        listx.sort()
        listy.sort()
        cropImg = img[listy[0]:listy[3], listx[0]:listx[3]]
        text = pytesseract.image_to_string(cropImg)
        print(text)
        cv2.imwrite("./region" + np.str(i) + ".jpg", cropImg)