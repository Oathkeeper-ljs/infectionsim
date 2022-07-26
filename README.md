# infectionsim
Simulate and visualize the spread of corona virus

## System design：
Everyone in the system is an entity. The virus spread process is simulated by regularly updating the status of each person in the area, the status of each person is counted to reflect the spread effect of the virus, and the spread effect is directly expressed through certain mapping rules. In the image, multiple days of images are then played continuously to form an animated demonstration of the spread of the virus.<br>

## Reasons not to apply off-the-shelf virus transmission models
1. Although the existing virus transmission model is relatively mature, compared with this epidemic, the use of hierarchical treatment methods cannot be well reflected in the existing transmission model, and choosing to simulate the behavior of each person is helpful. Counting the status of specific individuals can also more intuitively reflect the establishment of the infection chain, laying the foundation for the visibility of the subsequent simulation system.<br>
2. Even without using the ready-made virus propagation model, we can simulate the propagation process more scientifically by setting reasonable system parameters and propagation logic.<br>

## Experiment result（Part）
Seen in the repo：part_of_results.jpg

## Reference
https://github.com/matplotlib/matplotlib/issues/6338 <br>

https://gitee.com/crossin/snippet/tree/master/InfectSim <br>
