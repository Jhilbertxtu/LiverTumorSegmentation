'''=========================================================================

values for tumor:

Lower : 50
Upper: 100
X = 30
Y = 88
Z = 73

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
if len( sys.argv ) < 8:
  print("Usage: inputImage outputImage lowerThreshold upperThreshold seedX seedY seedZ expertSegmentation ");
  sys.exit( 1 )


#
# Read the image
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[1] )
image = reader.Execute();

#
# Blur using CurvatureFlowImageFilter
#
blurFilter = sitk.CurvatureFlowImageFilter()
blurFilter.SetNumberOfIterations( 5 )
blurFilter.SetTimeStep( 0.125 )
image = blurFilter.Execute( image )

#
# Set up ConnectedThresholdImageFilter for segmentation
#
segmentationFilter = sitk.NeighborhoodConnectedImageFilter()
segmentationFilter.SetLower( float(sys.argv[3]) )
segmentationFilter.SetUpper( float(sys.argv[4]) )
segmentationFilter.SetReplaceValue( 255 )

for i in range( 5, len(sys.argv)-1, 3 ):
  seed = [ int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2]) ]
  segmentationFilter.AddSeed( seed )
  print( "Adding seed at: ", seed, " with intensity: ", image.GetPixel(*seed) )

# Run the segmentation filter
image = segmentationFilter.Execute( image )
image[seed] = 255


#
# Read the segmentation
#
reader = sitk.ImageFileReader()
reader.SetFileName( sys.argv[8] )
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

