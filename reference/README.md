# numpy_comm: numpy direct comm. 

** Converting immgproc image into a numpy array: **

```python
import imgproc as ip
import matplotlib.pyplot as plt
import numpy as np

cam = ip.Camera(320, 240)
img = cam.grabImage()
iarr = np.zeros((240,320,3), 'uint8')
for x in range(320):
    for y in range(240):
        iarr[y,x] = img[x,y]
imgplot = plt.imshow(iarr)
plt.show()
```
