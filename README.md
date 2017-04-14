# LiverTumorSegmentation
Python Code for 3D segmentation of liver tumors in 3D MRI scans+ Volume calculation


================ READ ME ==================
 
 HOW TO RUN CODE:
 
 The code takes in 8 arguments:
 
 Argument 1: Name of .py file (in this case, tumor_segmentation.py which can be found under the finalcode directory)
 Argument 2: Input image (in this case Patient01Homo.mha, which can be found under the images directory)
 Argument 3: Name of output file (You can pick this one, I usually just do output.mha)
 Argument 4: Lower threshold for removing unwanted tissue (in this case 50)
 Argument 5: Upper threshold for removing unwanted tissue (in this case 90)
 Argument 6: Lower threshold for segmenting the tumor (In this case 2545)
 Argument 7: Upper threshold for segmenting the tumor (In this case 2550)
 Argument 8: Expert Segmentation Image file (In this case expert_seg.mha, found in the images directory)
 
 HERE IS THE LINE I USE TO RUN THE CODE:
 
 ipython tumor_segmentation.py Patient01homo.mha output.mha 50 90 2545 2550 expert_seg.mha
 
==============================================================================================

WHERE IS EVERYTHING?

In this final project directory you will find four folders:

IMAGE DIRECTORY: 

This directory has the image that is being segmented (named Patient01Homo.mha) and 
the expert segmentation that came with the dataset (named expert_seg.mha)

OUTPUT DIRECTORY:

This directory has the final segmentation image that I got from running my code (named output.mha)

OLDTRIES DIRECTORY:

I used a bunch of different approaches to get the segmentation that I got. Those older tries can be found
under this directory (incase you were curious to see what I did). They are named neighborhood_connected.py
and watershed.py. 

They don't have a good enough accuracy, but I thought you might wan to take a look.

FINALCODE DIRECTORY:

This is the final version of my code, i.e. the code you should run to get the results I got that I talk about below


==============================================================================================

SEGMENTATION CODE EXPLANATION:

When I was presenting my slides on Tuesday I mentioned that I was having trouble with the watershed segmentation going 
all the way out to the boundaries of the tumor.

In order to fix this, I ended up using the ThresholdImageFilter function from simpleITK.

The reason I used this filter is because it gave me the option to set everything outside of a threshold to black
while keeping the pixel values for everything inside the threshold the same.

I got a lot of spiky edges after this filter so I used the CurvatureFlowImageFilter to smooth out the image. 

Since the pixel values that were left are very close to each other, I used a watershed filter in order to segment
out the tumor.

After segmenting out the tumor, I set the values of the tumor to 255 and everything else to black (0) using a BinaryThresholdImageFilter

==============================================================================================

VALIDATION CODE EXPLANATION:

In order to figure out how accurate my segmentation was I did the following:

STEP ONE:

I took the expert segmentation from the dataset and set the voxel values to 255.
Using the LabelShapeStatisticsImageFilter I counted the number of voxels in the segmentation.
I got the spacing between the voxels using image.GetSpacing(), and by multiplying the spacing between
the voxels I got the volume of one pixel.
Then, I calculated the total volume of the expert segmentation of the tumor but multiplying the volume of one voxel
to the total number of voxels in the expert segmentation.


STEP TWO:

Using the BinaryThresholdImageFilter, I set the values of my segmentation and the expert segmentation to 127.


In order to calculate the FALSE NEGATIVES:

Using the AddImageFilter, I added the voxel values of the expert segmentation to the voxel values of my segmentation.
Then, using BinaryThresholdImageFilter, I singled out the voxel values that overlapped (i.e. were 254).
Next, I calculated the number of voxels in the false negative segmentation and calculated it's total volume.
Finally, in order to find the false negative error rate I used the following formula:

FALSE NEGATIVE ERROR RATE: (EXPERT SEGMENTATION VOLUME - FALSE NEGATIVE VOLUME) / EXPERT SEGMENTATION VOLUME

I got a false negative error rate of: 0.26, which is a big different from the 0.35 i was getting before.


In order to calculate the FALSE POSITIVES:

The idea with false positive is to find parts that were segmented in addition to the tumor.

Using the AddImageFilter, I added the voxel values of the expert segmentation back to the false negative segmentation.
Basically what happens in this case is this: 

Parts of my segmentation that didn't overlap with the expert segmentation remain at 127 pixel value from line 136.

Adding this back to the expert segmentation results in parts that had overlapped in line 136 to reset values to 125, 
because these values were at 254 and adding 127 back to it resets it to 125.

Finally, the parts of the tumor that were in the expert segmentation with 127 pixel value overlap with themselves again 
and have the value 254 at the end of this section.

THEREFORE! I can use BinaryThresholdImageFilter to segment out pixels that have a value of 127 (that were in my segmentation
that never overlapped with anything), and this way I get the false positives.

Finally, like the prior parts, I counted the number of voxels in this segmentation, multiplied by the volume of one voxel,
and used the following formula to get the error rate:

FALSE POSITIVE ERROR RATE: FALSE POSITIVE VOLUME / EXPERT SEGMENTATION VOLUME

I got a false positive error rate of: 0.14, which is pretty good if you ask me :) 

