'''=========================================================================
'
Values for Thresholding : lower 50, upper 90
Values for Watershed/getting the tumor: lower 2545 upper 2550

'
'========================================================================='''

from __future__ import print_function
from __future__ import division

import SimpleITK as sitk
import sys
import os

#
# Check Command Line
#
if len( sys.argv ) < 7:
  print("Usage: inputImage outputImage lowerThreshold1 upperThreshold1 lowerThreshold2 upperThreshold2 expertSegmentation ");
  sys.exit( 1 )


#
# Read the image
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[1] )
image = reader.Execute();




# Set up ThresholdImageFilter to remove large unwanted tissue areas

Thresholdfilter = sitk.ThresholdImageFilter()
Thresholdfilter.SetLower( float(sys.argv[3]) )
Thresholdfilter.SetUpper( float(sys.argv[4]) )
Thresholdfilter.SetOutsideValue( 0 )


# Run the Threshold filter
image = Thresholdfilter.Execute( image )

#
# Blur using CurvatureFlowImageFilter to smooth out the rough edges after ThresholdImageFilter
#
blurFilter = sitk.CurvatureFlowImageFilter()
blurFilter.SetNumberOfIterations( 5 )
blurFilter.SetTimeStep( 0.125 )
image = blurFilter.Execute( image )

#
# Setup and Execute Watershed Filter
#

level=10

image = sitk.GradientMagnitude(image)

watershedfilter = sitk.MorphologicalWatershedImageFilter ()
watershedfilter.SetLevel(level)
watershedfilter.SetMarkWatershedLine(True)
watershedfilter.SetFullyConnected(False)
image = watershedfilter.Execute( image )

#
# Set up BinaryThresholdImageFilter for segmenting the tumor
#

segmentationFilter = sitk.BinaryThresholdImageFilter()
segmentationFilter.SetLowerThreshold( float(sys.argv[5]) )
segmentationFilter.SetUpperThreshold( float(sys.argv[6]) )
segmentationFilter.SetInsideValue( 255 )
segmentationFilter.SetOutsideValue( 0 )


# Run the segmentation filter
image = segmentationFilter.Execute( image )

#### END OF SEGMENTATION ALGORITHM ####

### VERIFICATION PART ####

#
# Set up BinaryThresholdImageFilter to set My Segmentation Pixel Values to 127
#
segmentationFilterSecond = sitk.BinaryThresholdImageFilter()
segmentationFilterSecond.SetLowerThreshold( 250 )
segmentationFilterSecond.SetUpperThreshold( 255 )
segmentationFilterSecond.SetInsideValue( 127 )
segmentationFilterSecond.SetOutsideValue( 0 )


# Run the segmentation filter
my_segmentation = segmentationFilterSecond.Execute( image )

#
# Read the segmentation
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[7] )
expert_segm = reader.Execute();

#
# Set up BinaryThresholdImageFilter to set Expert Segmentation pixel values to white
#
segmentationFilterExp = sitk.BinaryThresholdImageFilter()
segmentationFilterExp.SetLowerThreshold( 0 )
segmentationFilterExp.SetUpperThreshold( 1000000000)
segmentationFilterExp.SetInsideValue( 0 )
segmentationFilterExp.SetOutsideValue( 255 )


# Run the segmentation filter
expert_segm = segmentationFilterExp.Execute( expert_segm )

#
# Set up BinaryThresholdImageFilter for segmentation
#
segmentationFilterExpTwo = sitk.BinaryThresholdImageFilter()
segmentationFilterExpTwo.SetLowerThreshold( 0 )
segmentationFilterExpTwo.SetUpperThreshold( 1000000000)
segmentationFilterExpTwo.SetInsideValue( 0 )
segmentationFilterExpTwo.SetOutsideValue( 127 )


# Run the segmentation filter
expert_segm_two = segmentationFilterExpTwo.Execute( expert_segm )


# Add the pixel values of images together

addFilter = sitk.AddImageFilter()

falsenegative = addFilter.Execute(my_segmentation, expert_segm_two)

falsepositive = addFilter.Execute(falsenegative, expert_segm_two)

#
# Set up BinaryThresholdImageFilter for False Negative
#
segmentationFilterNeg = sitk.BinaryThresholdImageFilter()
segmentationFilterNeg.SetLowerThreshold( 200 )
segmentationFilterNeg.SetUpperThreshold( 255)
segmentationFilterNeg.SetInsideValue( 255 )
segmentationFilterNeg.SetOutsideValue( 0 )


# Run the segmentation filter
falsenegative = segmentationFilterNeg.Execute( falsenegative )

#
# Set up BinaryThresholdImageFilter for False Positive
#
segmentationFilterPos = sitk.BinaryThresholdImageFilter()
segmentationFilterPos.SetLowerThreshold( 126 )
segmentationFilterPos.SetUpperThreshold( 127)
segmentationFilterPos.SetInsideValue( 255 )
segmentationFilterPos.SetOutsideValue( 0 )


# Run the segmentation filter
falsepositive = segmentationFilterPos.Execute( falsepositive )


#
# Find volumes:
#
inside_value = 0
outside_value = 255

# Volume of the false negative areas
label_shape_analysis_neg = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis_neg.SetBackgroundValue(inside_value)
label_shape_analysis_neg.Execute(falsenegative)

m = label_shape_analysis_neg.GetNumberOfPixels(outside_value)

v_my_segmentation_neg = reduce(lambda x, y: x*y, falsenegative.GetSpacing())

volume_mine_neg = m * v_my_segmentation_neg

# Volume of false positive areas

label_shape_analysis_pos = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis_pos.SetBackgroundValue(inside_value)
label_shape_analysis_pos.Execute(falsepositive)

l = label_shape_analysis_pos.GetNumberOfPixels(outside_value)

v_my_segmentation_pos = reduce(lambda x, y: x*y, falsepositive.GetSpacing())

volume_mine_pos = l * v_my_segmentation_pos


#Volume of Expert segmentation
label_shape_analysis_Expert = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis_Expert.SetBackgroundValue(inside_value)
label_shape_analysis_Expert.Execute(expert_segm)

n = label_shape_analysis_Expert.GetNumberOfPixels(outside_value)

v_expert_segmentation = reduce(lambda x, y: x*y, expert_segm.GetSpacing())

volume_expert = n * v_expert_segmentation

#Volume of My segmentation
label_shape_analysis_Mine = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis_Mine.SetBackgroundValue(inside_value)
label_shape_analysis_Mine.Execute(image)

p = label_shape_analysis_Mine.GetNumberOfPixels(outside_value)

v_my_segmentation = reduce(lambda x, y: x*y, image.GetSpacing())

volume_mine = p * v_my_segmentation


print("Number of Pixels in my segmentation is: {0:.2f}".format(label_shape_analysis_Mine.GetNumberOfPixels(outside_value)))
print("Number of Pixels in the expert segmentation is: {0:.2f}".format(label_shape_analysis_Expert.GetNumberOfPixels(outside_value)))
print("Number of False Poisitive Pixels is: {0:.2f}".format(label_shape_analysis_pos.GetNumberOfPixels(outside_value)))
print("Number of False Negative Pixels is: {0:.2f}".format(label_shape_analysis_neg.GetNumberOfPixels(outside_value)))
print("-----------------------------------------------")
print("My segmentation volume is: {0:.2f}".format(v_my_segmentation))
print("Expert Segmentation Volume is: {0:.2f}".format(volume_expert))
print("Volume of False Negative is: {0:.2f}".format(volume_mine_neg))
print("Volume of False Positive Is: {0:.2f}".format(volume_mine_pos))
print("-----------------------------------------------")
print("False Negative Rate is: {0:.2f}".format((volume_expert-volume_mine_neg)/volume_expert))
print("-----------------------------------------------")
print("False Positive Rate is: {0:.2f}".format(volume_mine_pos/volume_expert))

#
# Write out the result
#
writer = sitk.ImageFileWriter()
writer.SetFileName( sys.argv[2] )
writer.Execute( image )


if ( not "SITK_NOSHOW" in os.environ ):
  sitk.Show( image, "WatershedSegmentation" )

