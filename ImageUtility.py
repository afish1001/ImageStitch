import numpy as np
import cv2
from scipy.stats import mode

class Method():
    outputAddress = "result/"
    isEvaluate = True
    evaluateFile = "evaluate.txt"
    isPrintLog = True
    parallelMode = "None"   # "CPU","GPU"

    def printAndWrite(self, content):
        if self.isPrintLog:
            print(content)
        if self.isEvaluate:
            f = open(self.outputAddress + self.evaluateFile, "a")
            f.write(content)
            f.write("\n")
            f.close()

    def getROIRegion(self, image, direction="horizontal", order="first", searchLength=150, searchLengthForLarge=-1):
        '''对原始图像裁剪感兴趣区域
        :param originalImage:需要裁剪的原始图像
        :param direction:拼接的方向
        :param order:该图片的顺序，是属于第一还是第二张图像
        :param searchLength:搜索区域大小
        :param searchLengthForLarge:对于行拼接和列拼接的搜索区域大小
        :return:返回感兴趣区域图像
        :type searchLength: np.int
        '''
        row, col = image.shape[:2]
        if direction == "horizontal" or direction == 2:
            if order == "first":
                if searchLengthForLarge == -1:
                    roiRegion = image[:, col - searchLength:col]
                elif searchLengthForLarge > 0:
                    roiRegion = image[row - searchLengthForLarge:row, col - searchLength:col]
            elif order == "second":
                if searchLengthForLarge == -1:
                    roiRegion = image[:, 0: searchLength]
                elif searchLengthForLarge > 0:
                    roiRegion = image[0:searchLengthForLarge, 0: searchLength]
        elif direction == "vertical" or direction == 1:
            if order == "first":
                if searchLengthForLarge == -1:
                    roiRegion = image[row - searchLength:row, :]
                elif searchLengthForLarge > 0:
                    roiRegion = image[row - searchLength:row, col - searchLengthForLarge:col]
            elif order == "second":
                if searchLengthForLarge == -1:
                    roiRegion = image[0: searchLength, :]
                elif searchLengthForLarge > 0:
                    roiRegion = image[0: searchLength, 0:searchLengthForLarge]

    def getOffsetByRansac(self, kpsA, kpsB, matches, offsetEvaluate=100):
        totalStatus = False
        ptsA = np.float32([kpsA[i] for (_, i) in matches])
        ptsB = np.float32([kpsB[i] for (i, _) in matches])
        if len(matches) == 0:
            return (totalStatus, [0, 0], 0)
        # 计算视角变换矩阵
        # H1 = cv2.getAffineTransform(ptsA, ptsB)
        # print("H1")
        # print(H1)
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, 3, 0.9)
        trueCount = 0
        for i in range(0, len(status)):
            if status[i] == True:
                trueCount = trueCount + 1
        if trueCount >= offsetEvaluate:
            totalStatus = True
            adjustH = H.copy()
            adjustH[0, 2] = 0;adjustH[1, 2] = 0
            adjustH[2, 0] = 0;adjustH[2, 1] = 0
            return (totalStatus ,[np.round(np.array(H).astype(np.int)[1,2]) * (-1), np.round(np.array(H).astype(np.int)[0,2]) * (-1)], adjustH)
        else:
            return (totalStatus, [0, 0], 0)

    def detectAndDescribe(self, image, featureMethod):
        '''
    	计算图像的特征点集合，并返回该点集＆描述特征
    	:param image:需要分析的图像
    	:return:返回特征点集，及对应的描述特征
    	'''
        # 建立SIFT生成器
        if featureMethod == "sift":
            descriptor = cv2.xfeatures2d.SIFT_create()
        elif featureMethod == "surf":
            descriptor = cv2.xfeatures2d.SURF_create()
        elif featureMethod == "orb":
            descriptor = cv2.ORB_create(5000000)

        # 检测SIFT特征点，并计算描述子
        (kps, features) = descriptor.detectAndCompute(image, None)

        # 将结果转换成NumPy数组
        kps = np.float32([kp.pt for kp in kps])

        # 返回特征点集，及对应的描述特征
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB, ratio):
        '''
        匹配特征点
        :param self:
        :param featuresA: 第一张图像的特征点描述符
        :param featuresB: 第二张图像的特征点描述符
        :param ratio: 最近邻和次近邻的比例
        :return:返回匹配的对数
        '''
        # 建立暴力匹配器
        matcher = cv2.DescriptorMatcher_create("BruteForce")

        # 使用KNN检测来自A、B图的SIFT特征匹配对，K=2，返回一个列表
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []
        for m in rawMatches:
        # 当最近距离跟次近距离的比值小于ratio值时，保留此匹配对
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                # 存储两个点在featuresA, featuresB中的索引值
                matches.append((m[0].trainIdx, m[0].queryIdx))
        self.printAndWrite("  The number of matches is " + str(len(matches)))
        return matches

    def getOffsetByMode(self, kpsA, kpsB, matches, offsetEvaluate = 10):
        totalStatus = True
        if len(matches) == 0:
            totalStatus = False
            return (totalStatus, [0, 0])
        dxList = []; dyList = [];
        for trainIdx, queryIdx in matches:
            ptA = (kpsA[queryIdx][1], kpsA[queryIdx][0])
            ptB = (kpsB[trainIdx][1], kpsB[trainIdx][0])
            # dxList.append(int(round(ptA[0] - ptB[0])))
            # dyList.append(int(round(ptA[1] - ptB[1])))
            dxList.append(int(ptA[0] - ptB[0]))
            dyList.append(int(ptA[1] - ptB[1]))
        dxMode, count = mode(np.array(dxList), axis=None)
        dyMode, count = mode(np.array(dyList), axis=None)
        dx = int(dxMode); dy = int(dyMode)
        # Evaluate
        maxNum = len(dxList)
        num = 0
        for i in range(0, maxNum):
            if dxList[i] == dx and dyList[i] == dy:
                num += 1
        if num < offsetEvaluate:
            totalStatus = False
        self.printAndWrite("  In Mode, The number of num is " + str(num) + " and the number of offsetEvaluate is "+str(offsetEvaluate))
        return (totalStatus, [dx, dy])

    def getROIRegionForIncreMethod(self, image, direction=1, order="first", searchRatio=0.1):
        row, col = image.shape[:2]
        roiRegion = np.zeros(image.shape, np.uint8)
        if direction == 1:
            searchLength = np.floor(row * searchRatio).astype(int)
            if order == "first":
                roiRegion = image[row - searchLength:row, :]
            elif order == "second":
                roiRegion = image[0: searchLength, :]
        elif direction == 2:
            searchLength = np.floor(col * searchRatio).astype(int)
            if order == "first":
                roiRegion = image[:, col - searchLength:col]
            elif order == "second":
                roiRegion = image[:, 0: searchLength]
        elif direction == 3:
            searchLength = np.floor(row * searchRatio).astype(int)
            if order == "first":
                roiRegion = image[0: searchLength, :]
            elif order == "second":
                roiRegion = image[row - searchLength:row, :]
        elif direction == 4:
            searchLength = np.floor(col * searchRatio).astype(int)
            if order == "first":
                roiRegion = image[:, 0: searchLength]
            elif order == "second":
                roiRegion = image[:, col - searchLength:col]
        return roiRegion