'''=========================================================================
'
Values for liver: upper 971, lower 970

VALUES FOR TUMOR: lower 6204 upper 6205

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
if len( sys.argv ) < 2:
  print("Usage: inputImage outputImage lowerThreshold upperThreshold expertSegmentation ");
  sys.exit( 1 )


#
# Read the image
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[1] )
image = reader.Execute();


#
# get spacing
#

sigma=image.GetSpacing()[0]
level=2

image = sitk.GradientMagnitude(image)

#
# Watershed
#

watershedfilter = sitk.MorphologicalWatershedImageFilter ()
watershedfilter.SetLevel(level)
watershedfilter.SetMarkWatershedLine(True)
watershedfilter.SetFullyConnected(False)
image = watershedfilter.Execute( image )


#
# Set up BinaryThresholdImageFilter for segmentation
#
segmentationFilter = sitk.BinaryThresholdImageFilter()
segmentationFilter.SetLowerThreshold( float(sys.argv[3]) )
segmentationFilter.SetUpperThreshold( float(sys.argv[4]) )
segmentationFilter.SetInsideValue( 255 )
segmentationFilter.SetOutsideValue( 0 )


# Run the segmentation filter
image = segmentationFilter.Execute( image )



#
# Read the segmentation
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[5] )
segm = reader.Execute();

#
# Set up BinaryThresholdImageFilter for segmentation
#
segmentationFilter = sitk.BinaryThresholdImageFilter()
segmentationFilter.SetLowerThreshold( 0 )
segmentationFilter.SetUpperThreshold( 1000000000)
segmentationFilter.SetInsideValue( 0 )
segmentationFilter.SetOutsideValue( 255 )


# Run the segmentation filter
segm = segmentationFilter.Execute( segm )



#
# Find Volume expert segmentation and my segmentation
#

inside_value = 0
outside_value = 255

label_shape_analysis = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis.SetBackgroundValue(inside_value)
label_shape_analysis.Execute(image)

label_shape_analysis_Expert = sitk.LabelShapeStatisticsImageFilter()
label_shape_analysis_Expert.SetBackgroundValue(inside_value)
label_shape_analysis_Expert.Execute(segm)

m = label_shape_analysis.GetNumberOfPixels(outside_value)
n = label_shape_analysis_Expert.GetNumberOfPixels(outside_value)



#Calculate volume of one voxel

v_expert_segmentation = reduce(lambda x, y: x*y, segm.GetSpacing())
v_my_segmentation = reduce(lambda x, y: x*y, image.GetSpacing())

# Calculate volume of segmentation:
volume_expert = n * v_expert_segmentation
volume_mine = m * v_my_segmentation

#label = label_shape_analysis.GetNumberOfLabels()
#print("labels is :" , label)
print("Number of Pixels is: {0:.2f}".format(label_shape_analysis.GetNumberOfPixels(outside_value)))
print("Number of Pixels is: {0:.2f}".format(label_shape_analysis_Expert.GetNumberOfPixels(outside_value)))
print("My segmentation volume is: {0:.2f}".format(volume_mine))
print("Expert Segmentation Volume is: {0:.2f}".format(volume_expert))
print("Error Rate is: {0:.2f}".format((2*(volume_expert - volume_mine)/(volume_mine+volume_expert))))


#
# Write out the result
#
writer = sitk.ImageFileWriter()
writer.SetFileName( sys.argv[2] )
writer.Execute( image )


if ( not "SITK_NOSHOW" in os.environ ):
  sitk.Show( image, "ConntectedThreshold" )

