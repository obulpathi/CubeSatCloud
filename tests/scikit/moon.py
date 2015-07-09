import matplotlib.pyplot as plt

from skimage import data
from skimage.exposure import rescale_intensity

import time

t1 = time.time()
image = data.moon()
# Rescale image intensity so that we can see dim features.
image = rescale_intensity(image, in_range=(50, 200))

t2 = time.time()
print (t2-t1)

# convenience function for plotting images
def imshow(image, **kwargs):
    plt.figure(figsize=(5, 4))
    plt.imshow(image, **kwargs)
    plt.axis('off')

#imshow(image)
#plt.title('original image')
