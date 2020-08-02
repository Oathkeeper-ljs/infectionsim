# infectionsim
模拟病毒的传播并实现其可视化

## 系统原理（思路）：
系统中的每个人都是一个实体，通过定时更新区域内的每个人状态来仿真病毒的传播过程，统计每个人的状态来反应病毒的传播效果，并通过一定的映射规则将传播效果直接的表现在图像中，之后将多天的图像连续播放来形成病毒的传播动画演示。<br>

## 不套用现成的病毒传播模型理由
1、虽然现有的病毒传播模型较为成熟，但相比这次疫情，采用分级救治的方法，不能很好的在现有的传播模型中有所体现，且选择模拟每个人的行为有助于统计具体的个体的状态，也能更直观地反映出传染链的建立，为后续的仿真系统可视性奠定了基础。<br>
2、即使不使用现成的病毒传播模型，我们通过设置合理的系统参数及传播逻辑，也能较为科学地对传播过程进行仿真。<br>

## 实验结果（部分）
![](https://https://github.com/Oathkeeper-ljs/infectionsim/blob/master/%E9%83%A8%E5%88%86%E5%AE%9E%E9%AA%8C%E7%BB%93%E6%9E%9C%E8%A1%A8%E6%A0%BC.png)
