# Semantic Segmentation
### Introduction
In this project road image pixel labes were classified using a Fully Convolutional Network (FCN).

[image1]: ./runs/1534447570.8183498/umm_000090.png "Good Example"
[image2]: ./runs/1534448426.3902185/uu_000011.png "Bad Example"


### Setup
##### GPU
`main.py` will check to make sure you are using GPU - if you don't have a GPU on your system, you can use AWS or another cloud computing platform.
##### Frameworks and Packages
Make sure you have the following is installed:
 - [Python 3](https://www.python.org/)
 - [TensorFlow](https://www.tensorflow.org/)
 - [NumPy](http://www.numpy.org/)
 - [SciPy](https://www.scipy.org/)
##### Dataset
Download the [Kitti Road dataset](http://www.cvlibs.net/datasets/kitti/eval_road.php) from [here](http://www.cvlibs.net/download.php?file=data_road.zip).  Extract the dataset in the `data` folder.  This will create the folder `data_road` with all the training a test images.

### Writeup
##### Implement
All of the required TODO functions were completed as required.
##### Run
Run the following command to run the project:
```
python main.py
```
**Note** If running this in Jupyter Notebook system messages, such as those regarding test status, may appear in the terminal rather than the notebook.

## Contemplation
A final model was produced through trial and error of both model architecture and hyperperameter tuning.

### My final model consisted of the following layers:

| Layer         		|     Description	        					| 
|:---------------------:|:---------------------------------------------:| 
| Input         		|  RGB image   							| 
| VGG16 Pretrained Layer     	| N/A 	|
| Atrous Convolution Dilation 1x1					|	1x1 stride, same padding, l2_regularization											|
| Atrous Convolution Dilation 3x3					|	1x1 stride, same padding, l2_regularization											|
| Atrous Convolution Dilation 6x6					|	1x1 stride, same padding, l2_regularization											|
| Atrous Convolution Dilation 1x1					|	1x1 stride, same padding, l2_regularization											|
| Convolution 1x1 of VGG_LAYER7_OUT					|	1x1 stride, same padding, l2_regularization											|
| Concatenation of Previous Layers	      	|  				|
| Convolution 1x1					|	1x1 stride, same padding, l2_regularization											|
| Convolution Transpose 2x2					|	2x2 stride, same padding, l2_regularization											|
| Convolution 1x1	of VGG_LAYER4_OUT				|	1x1 stride, same padding, l2_regularization											|
| Add Previos Two Convolutions |     |
| Convolution Transpose 2x2					|	2x2 stride, same padding, l2_regularization											|
| Convolution 1x1	of VGG_LAYER3_OUT				|	1x1 stride, same padding, l2_regularization											|
| Add Previos Two Convolutions |     |
| Convolution Transpose 2x2					|	2x2 stride, same padding, l2_regularization											|
| Convolution Transpose 2x2					|	2x2 stride, same padding, l2_regularization											|
| Convolution Transpose 2x2					|	2x2 stride, same padding, l2_regularization											|

An Adam optimizer was chosen for the network and used a scalled sum of the cross entropy loss and regularizar loss from the individual layers. 

## Results
The model can be consistently trained to a loss of roughly 0.06 across multiple runs. Overfitting issues begin to appear at about this level so the number of epochs was limited to 12 for each training run. As can be seen in the images below, there are instances where the network performs very well such as on a straight clean street whereas shadows tend to cause considerable issues.

![alt text][image1] ![alt text][image2]
