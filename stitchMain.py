from Stitcher import Stitcher
import cv2
import time
import glob
import os
import time

def stitchWithFeature():
    Stitcher.featureMethod = "surf"     # "sift","surf" or "orb"
    Stitcher.isGPUAvailable = True
    Stitcher.searchRatio = 0.75         # 0.75 is common value for matches
    Stitcher.offsetCaculate = "mode"    # "mode" or "ransac"
    Stitcher.offsetEvaluate = 3         # 40 menas nums of matches for mode, 4.0 menas  of matches for ransac
    Stitcher.roiRatio = 0.2             # roi length for stitching in first direction
    # Stitcher.fuseMethod = "fadeInAndFadeOut"
    Stitcher.fuseMethod = "notFuse"
    stitcher = Stitcher()
    startTime = time.time()

    # method = "featureSearchIncre";  Stitcher.direction = 1;  Stitcher.directIncre = 0;
    # projectAddress = "images\\iron"
    # outputAddress = "result\\" + method + "\\iron" + str.capitalize(Stitcher.fuseMethod) + "\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 50, stitcher.calculateOffsetForFeatureSearchIncre,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # method = "featureSearchIncre"; Stitcher.direction = 1;  Stitcher.directIncre = 1;
    # projectAddress = "images\\dendriticCrystal"
    # outputAddress = "result\\" + method + "\\dendriticCrystal" + str.capitalize(Stitcher.fuseMethod) + "\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 11, stitcher.calculateOffsetForFeatureSearchIncre,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # Stitcher.featureMethod = "surf"; Stitcher.searchRatio = 0.95; Stitcher.offsetEvaluate = 3;
    # method = "featureSearchIncre";  Stitcher.direction = 1;  Stitcher.directIncre = 1;
    # Stitcher.isEnhance = True;  # Stitcher.isClahe = True;
    # Stitcher.fuseMethod = "notFuse"
    # projectAddress = "images\\superalloyTurbineblade"
    # outputAddress = "result\\" + method + "\\superalloyTurbineblade" + str.capitalize(Stitcher.fuseMethod) + "\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # method = "featureSearchIncre"; Stitcher.direction = 4;  Stitcher.directIncre = 0;
    # projectAddress = "images\\zirconLarge"
    # outputAddress = "result\\" + method + "\\zirconLarge" + str.capitalize(Stitcher.fuseMethod) + "\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 96, stitcher.calculateOffsetForFeatureSearchIncre,
    #                         startNum=89, fileExtension="jpg", outputfileExtension="png")

    method = "featureSearchIncre"; Stitcher.direction = 4;  Stitcher.directIncre = 0;
    projectAddress = "images\\zirconLargeResized_4_INTER_AREA"
    outputAddress = "result\\" + method + "\\zirconLargeResized_4_INTER_AREA" + str.capitalize(Stitcher.fuseMethod) + "\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 97, stitcher.calculateOffsetForFeatureSearch,
                            startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # method = "featureSearch"; Stitcher.direction = 4;  Stitcher.directIncre = 0;
    # projectAddress = "images\\zirconSmall"
    # outputAddress = "result\\" + method + "\\zirconSmall" + str.capitalize(Stitcher.fuseMethod) + "\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 194, stitcher.calculateOffsetForFeatureSearch,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")
    endTime = time.time()
    print("Time Consuming = " + str(endTime - startTime))

def stitchWithPhase():
    method = "phaseCorrelate"
    Stitcher.fuseMethod = "notFuse"
    stitcher = Stitcher()
    projectAddress = "images\\zirconSmall"
    outputAddress = "result\\" + method + "\\zirconSmall" + str.capitalize(Stitcher.fuseMethod) + "\\"
    stitcher.imageSetStitch(projectAddress, outputAddress, 51, stitcher.calculateOffsetForPhaseCorrleate,
                            startNum=43, fileExtension="jpg", outputfileExtension="jpg")
    Stitcher.phase.shutdown()

def paperExperiments():

    Stitcher.featureMethod = "orb"     # "sift","surf" or "orb"
    Stitcher.isGPUAvailable = False
    Stitcher.searchRatio = 0.75         # 0.75 is common value for matches
    Stitcher.offsetCaculate = "mode"    # "mode" or "ransac"
    Stitcher.offsetEvaluate = 3         # 40 menas nums of matches for mode, 4.0 menas  of matches for ransac
    Stitcher.roiRatio = 0.2             # roi length for stitching in first direction
    Stitcher.fuseMethod = "notFuse"
    # Stitcher.fuseMethod = "trigonometric"
    stitcher = Stitcher()

    method = "featureSearchIncre";  Stitcher.direction = 1;  Stitcher.directIncre = 0;
    projectAddress = "images\\paperExperiments\\iron"
    outputAddress = "result\\paperExperiments\\iron\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                            startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    method = "featureSearchIncre";Stitcher.direction = 4; Stitcher.directIncre = 0;
    projectAddress = "images\\paperExperiments\\zirconBSE"
    outputAddress = "result\\paperExperiments\\zirconBSE\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                                       startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    method = "featureSearchIncre";Stitcher.direction = 4;  Stitcher.directIncre = 0;
    projectAddress = "images\\paperExperiments\\zirconCL"
    outputAddress = "result\\paperExperiments\\zirconCL\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                            startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    method = "featureSearchIncre";Stitcher.direction = 4; Stitcher.directIncre = 0;
    projectAddress = "images\\paperExperiments\\zirconREM"
    outputAddress = "result\\paperExperiments\\zirconREM\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                                       startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    method = "featureSearchIncre";Stitcher.direction = 4;  Stitcher.directIncre = 0;
    projectAddress = "images\\paperExperiments\\zirconTEM"
    outputAddress = "result\\paperExperiments\\zirconTEM\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                            startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    method = "featureSearchIncre"; Stitcher.direction = 1;  Stitcher.directIncre = 1;
    projectAddress = "images\\paperExperiments\\dendriticCrystal"
    outputAddress = "result\\paperExperiments\\dendriticCrystal\\"
    stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearchIncre,
                            startNum=1, fileExtension="jpg", outputfileExtension="jpg")


    # # Search
    # method = "featureSearch";  Stitcher.direction = 1;  Stitcher.directIncre = 0;
    # projectAddress = "images\\paperExperiments\\iron"
    # outputAddress = "result\\paperExperiments\\iron\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearch,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")
    #
    # method = "featureSearch";Stitcher.direction = 4; Stitcher.directIncre = 0;
    # projectAddress = "images\\paperExperiments\\zirconBSE"
    # outputAddress = "result\\paperExperiments\\zirconBSE\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearch,
    #                                    startNum=1, fileExtension="jpg", outputfileExtension="jpg")
    #
    # method = "featureSearch";Stitcher.direction = 4;  Stitcher.directIncre = 0;
    # projectAddress = "images\\paperExperiments\\zirconCL"
    # outputAddress = "result\\paperExperiments\\zirconCL\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearch,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # method = "featureSearchIncre";Stitcher.direction = 4; Stitcher.directIncre = 0;
    # projectAddress = "images\\paperExperiments\\zirconREM"
    # outputAddress = "result\\paperExperiments\\zirconREM\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 10, stitcher.calculateOffsetForFeatureSearchIncre,
    #                                    startNum=1, fileExtension="jpg", outputfileExtension="jpg")
    #
    # method = "featureSearch";Stitcher.direction = 4;  Stitcher.directIncre = 0;
    # projectAddress = "images\\paperExperiments\\zirconTEM"
    # outputAddress = "result\\paperExperiments\\zirconTEM\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 10, stitcher.calculateOffsetForFeatureSearchIncre,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")

    # method = "featureSearch"; Stitcher.direction = 1;  Stitcher.directIncre = 1;
    # projectAddress = "images\\paperExperiments\\dendriticCrystal"
    # outputAddress = "result\\paperExperiments\\dendriticCrystal\\"
    # stitcher.imageSetStitchWithMutiple(projectAddress, outputAddress, 1, stitcher.calculateOffsetForFeatureSearch,
    #                         startNum=1, fileExtension="jpg", outputfileExtension="jpg")


if __name__=="__main__":
    paperExperiments()
    #stitchWithFeature()