#!/usr/bin/env python
# coding: utf-8

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pylab import mpl
# In[1]:

# 设定参数
area_size = 100                   # 区域大小
num_total = 100000                # 总人口数
bed_in_hos = 2000                 # 医院床位
bed_in_mhos = 10000               # 方舱床位

ep_dis = (5, 2)                   # 潜伏期分布 正态分布（均值，方差）
inci_dis = (10, 3)                # 发病期分布 正态分布（均值，方差）
day_infec_start = -1              # 传染起始日
trans_rate = 0.5                  # 传播概率
immune_rate = 0.1                 # 免疫概率
intence_rate = 0.05               # 重症概率
death_rate = 0.1                  # 病亡概率
heal_rate = 0.95                  # 救治概率

in_hos_rate = 0.1                 # 入院意愿
in_mhos_rate = 0.99               # 进入方舱概率
mask_rate = 0                     # 戴口罩意愿
out_rate = 0.8                    # 出行意愿
stay_rate = 0.8                   # 常住区域概率
getnear_rate = 0.95               # 周边出行概率
contact_rate = 0.5                # 接触比例
alarm_num = 1000                  # 警戒人数
cancel_time = 999                 # 解除时间

# In[2]:


list_total = []                  # 总人员列表
list_in_hos = []                 # 住院人员列表
list_in_mhos = []                # 方舱人员列表
list_deadman = []                # 病亡人员列表

list_area_dis = [[[] for i in range(area_size)] for j in range(area_size)]           # 区域分布列表


class man():                                                          # 人
    def __init__(self, i):
        self.uid = i
        self.x, self.y = self.random_locate()
        self.localarea = set()                                       # 常住区域
        self.num_localarea = random.randint(3, 6)                    # 常住区域数量
        list_area_dis[self.x][self.y].append(self)                   # 区域分布列表
        self.localarea.add((self.x, self.y))                         # 常住区域
        self.is_infected = False                                     # 已感染
        self.infection = False                                       # 传染性
        self.immune = random.random() < immune_rate                  # 免疫
        self.is_inhos = False                                        # 已入院
        self.is_inmhos = False                                       # 已进方舱
        self.state = '健康'                                          # 身体状况
        self.day_after_infection = 0                                 # 感染后天数
        self.latency_period = 0                                      # 潜伏期
        self.disease_period = 0                                      # 发病期
        self.infect_period = 0                                       # 传染期

    def random_gauss(self, sigma):
        ga = 101
        while ga >= 100 or ga < 0 :
            ga = random.gauss(50,sigma)
        return int(ga)

    def random_locate(self):                                         # 随机位置
        # 85%人分布在25%区域
        if random.random() < 0.6:                    # 80%的人在中间
            px = self.random_gauss(15)
            py = self.random_gauss(15)
        else:                                        # 5%的人可能到中间，剩余15%到其他位置
            px = random.randint(0, area_size - 1)
            py = random.randint(0, area_size - 1)
        return px, py

    def update_locate(self, in_his=False):                               # 更新位置
        # 从区域分布列表中移除
        list_area_dis[self.x][self.y].remove(self)
        if in_his:
            # 在常住区域移动
            pos = random.choice(list(self.localarea))
        else:
            # 去新区域
            if random.random() < getnear_rate:
                # 在周边九宫格移动
                off_x = random.randint(-1, 1)
                off_y = random.randint(-1, 1)
                pos = (max(min(self.x + off_x, area_size - 1), 0), max(min(self.y + off_y, area_size - 1), 0))
            else:
                # 完全随机位置
                pos = self.random_locate()
        self.x, self.y = pos
        # 添加进入区域分布列表
        list_area_dis[self.x][self.y].append(self)
        if len(self.localarea) < self.num_localarea:
            self.localarea.add((self.x, self.y))

    def getout(self):                                               # 出行
        if not self.is_inhos and not self.is_inmhos and random.random() < out_rate:
            if len(self.localarea) < self.num_localarea:
                self.update_locate()
            else:
                if random.random() < stay_rate:
                    # 在常住区域移动
                    self.update_locate(True)
                else:
                    # 去新区域
                    self.update_locate()

    def be_infected(self):                                                                      # 被传染
        self.is_infected = True                                                                 # 已感染
        self.state = '潜伏'                                                                     # 身体状况
        self.latency_period = random.gauss(ep_dis[0], ep_dis[1])                                # 潜伏期
        self.disease_period = self.latency_period + random.gauss(inci_dis[0], inci_dis[1])      # 发病期
        self.infect_period = self.latency_period + day_infec_start                              # 传染期

    def infect_others(self):                                                                    # 传染
        others = list_area_dis[self.x][self.y]
        count = len(others)
        #与在传染期接触的其他人
        touch = random.sample(others, int(count * contact_rate) + 1)
        for h in touch:
            infect_rate = trans_rate
            if random.random() < mask_rate:
                # 概率降低到5%
                infect_rate *= 0.05
            if (h.state == '健康' or h.state == '康复') and not h.immune and random.random() < infect_rate:
                h.be_infected()

    def disease_develop(self):                                                     # 病情发展
        if not self.is_infected:
            return
        self.day_after_infection += 1
        if not self.infection and self.day_after_infection >= self.infect_period:
            self.infection = True
        if self.state == '潜伏' and self.day_after_infection >= self.latency_period:
            self.state = '发病'
        if self.state == '发病':
            if bed_in_mhos > 0:
                # 分级收治，轻症进方舱
                if not self.is_inhos and not self.is_inmhos and random.random() < in_mhos_rate and len(list_in_mhos) < bed_in_mhos:
                    # 进方舱
                    self.is_inmhos = True
                    list_in_mhos.append(self)
                    list_area_dis[self.x][self.y].remove(self)
            else:
                if not self.is_inhos and len(list_in_hos) < bed_in_hos and random.random() < in_hos_rate:
                    self.is_inhos = True
                    list_in_hos.append(self)
                    if self.is_inmhos:
                        self.is_inmhos = False
                        list_in_mhos.remove(self)
                    else:
                        list_area_dis[self.x][self.y].remove(self)
            if self.day_after_infection >= self.disease_period:
                self.recovery()
            elif random.random() < intence_rate:
                self.state = '重症'                                      # 转重症
        if self.state == '重症':
            dead_rate = death_rate
            if self.is_inhos:
                dead_rate *= (1 - heal_rate)
            elif len(list_in_hos) < bed_in_hos:
                dead_rate *= (1 - heal_rate)
                self.is_inhos = True
                list_in_hos.append(self)
                if self.is_inmhos:
                    self.is_inmhos = False
                    list_in_mhos.remove(self)
                else:
                    list_area_dis[self.x][self.y].remove(self)
            if random.random() < dead_rate:
                self.dead()
            elif self.day_after_infection >= self.disease_period:
                self.state = '发病'
                self.disease_period += 5

    def dead(self):                                               # 病亡
        self.state = '病亡'
        self.is_infected = False
        self.infection = False
        if self.is_inhos:
            self.is_inhos = False
            list_in_hos.remove(self)
        if self.is_inmhos:
            self.is_inmhos = False
            list_in_mhos.remove(self)
        list_total.remove(self)                                  # 从总人员列表中移除
        list_deadman.append(self)

    def recovery(self):                                              # 康复
        self.state = '康复'
        self.is_infected = False
        self.infection = False
        if self.is_inhos:
            self.is_inhos = False
            list_in_hos.remove(self)
            list_area_dis[self.x][self.y].append(self)
        if self.is_inmhos:
            self.is_inmhos = False
            list_in_mhos.remove(self)
            list_area_dis[self.x][self.y].append(self)

# 初始化区域
x = np.zeros(area_size * area_size)
y = np.zeros(area_size * area_size)
for i in range(area_size):
    for j in range(area_size):
        x[i * area_size + j] = i
        y[i * area_size + j] = j

# 初始化人群
for i in range(num_total):
    list_total.append(man(i))

# 产生零号病人
h = list_total[0]
h.is_infected = True

# In[3]

healthy_curve = []                                                # 健康曲线
infection_curve = []                                              # 感染曲线
recovery_curve = []                                               # 康复曲线
dead_curve = []                                                   # 病亡曲线
hos_curve = []                                                    # 医院曲线
mhos_curve = []                                                   # 方舱曲线

def update(t):                                                      # 状态更新函数
    if t!=0:
        print(t, end='')
    list_infected_man = []
    # 在list_total中的所有人都出行、病情发展、统计传染性
    for h in list_total:
        h.getout()
        h.disease_develop()
        # 具有传染性 进入传染名单
        if h.infection and not h.is_inhos and not h.is_inmhos:
            list_infected_man.append(h)
    # 传染名单内的人传染别人
    for h in list_infected_man:
        h.infect_others()

    # 统计各状态人数
    jk = gr = kf = bw = fb = 0
    for h in list_total:
        if h.state == '健康':
            jk += 1
        elif h.state == '潜伏' or h.state == '发病' or h.state == '重症':
            gr += 1
            if h.state != '潜伏':
                fb += 1
        elif h.state == '康复':
            kf += 1
        elif h.state == '病亡':
            bw += 1
    healthy_curve.append(jk)
    infection_curve.append(gr)
    recovery_curve.append(kf)
    dead_curve.append(len(list_deadman))
    hos_curve.append(len(list_in_hos))
    mhos_curve.append(len(list_in_mhos))

    # 改变人群重视程度
    if fb > alarm_num:
        print('!', end='')
        global mask_rate
        global out_rate
        global contact_rate
        global in_hos_rate
        mask_rate = 0.9
        out_rate = 0.05
        contact_rate = 0.2
        in_hos_rate = 1
    if t > cancel_time:
        mask_rate = 0.2
        out_rate = 0.7
        contact_rate = 0.4

    if t != 0:
        print(' ',end='')

    # 根据感染人数占该区域总人数的百分比来改变区域颜色
    for i in range(area_size):
        for j in range(area_size):
            count = len(list_area_dis[i][j])
            sizes[i * area_size + j] = count
            num_infected = 0
            num_recovery = 0
            for h in list_area_dis[i][j]:
                if h.is_infected:
                    num_infected += 1
                elif h.state == '康复':
                    num_recovery += 1
            if count > 0:
                colors[i * area_size + j] = '#%s%s00' % ('{:02x}'.format(int(num_infected / count * 255)),
                                                    '{:02x}'.format(int(num_recovery / count * 255)))
            else:
                colors[i * area_size + j] = '#000000'

    sc.set_sizes(sizes)
    sc.set_color(colors)
    title.set_text(t)

    return sc,

sizes = np.zeros(area_size * area_size)
# 每个点的大小由该区域的人数决定
for i in range(area_size):
    for j in range(area_size):
        sizes[i * area_size + j] = len(list_area_dis[i][j])
colors = np.zeros(area_size * area_size, dtype='U7')
colors[:] = '#000000'
# 画图
fig, ax = plt.subplots(figsize=(16, 16))
plt.xticks([])
plt.yticks([])

title = ax.text(0.1, 0.1, '', bbox={'facecolor': 'w', 'alpha': 0.5, 'pad': 15},
                transform=ax.transAxes, ha="center", fontsize=20)
sc = ax.scatter(x, y, s=sizes, c=colors, alpha=0.5)

print("显示的数字表示当前仿真的时间（单位：天），感叹号表示当前感染人数大于警戒人数，已引起社会人群重视。")
print("当前警戒人数：",alarm_num)
# 制作动画 100天 间隔100ms
ani = animation.FuncAnimation(fig, update, frames=100, interval=100, blit=True, repeat=False)
# 将动画数据写入HTML文件
with open("test1.html", "w") as f:
    print(ani.to_html5_video(), file=f)

# In[4]:

# 绘制曲线图

font = mpl.font_manager.FontProperties(fname='heiti.TTF', size=15)

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 显示健康人数的曲线图
plt.figure(figsize=(16, 12))
plt.plot(healthy_curve, 'b')
plt.plot(infection_curve, 'r')
plt.plot(recovery_curve, 'g')
plt.plot(dead_curve, 'k')
plt.plot(hos_curve, 'c')
plt.plot(mhos_curve, 'y')
plt.legend(['健康', '感染', '康复', '病亡', '医院', '方舱'], prop=font)
# plt.legend(['健康', '感染', '康复', '病亡', '医院'], prop=font)
plt.title('显示健康人数的曲线图')
plt.show()

# In[5]:

# 不显示健康人数的曲线图
plt.figure(figsize=(16, 7))
plt.xlim((0, 100))
plt.ylim((0, 100000))
plt.plot(recovery_curve, 'g')
plt.plot(infection_curve, 'r')
plt.plot(dead_curve, 'k')
plt.plot(hos_curve, 'c')
plt.plot(mhos_curve, 'y')
plt.legend(['康复', '感染', '病亡', '医院', '方舱'], prop=font)
# plt.legend(['康复', '感染', '病亡', '医院'], prop=font)
plt.title('不显示健康人数的曲线图')
plt.show()

# In[6]:
print('\n')
print("患病人数：",(recovery_curve[-1] + dead_curve[-1]),"\n康复人数：",
      recovery_curve[-1],"\n死亡人数：", dead_curve[-1],"\n病死率：" ,
      '%.3f' % (dead_curve[-1]*100 / (recovery_curve[-1] + dead_curve[-1])),'%')
print("仿真结束")

# In[7]:

# 绘制曲线动画

fig2, ax2 = plt.subplots(figsize=(16, 12))

line1, = ax2.plot(healthy_curve, 'b')
line2, = ax2.plot(infection_curve, 'r')
line3, = ax2.plot(recovery_curve, 'g')
line4, = ax2.plot(dead_curve, 'k')
line5, = ax2.plot(hos_curve, 'c')
line6, = ax2.plot(mhos_curve, 'y')
plt.legend([ '健康','感染', '康复', '病亡', '医院', '方舱'], prop=font)

def go(t):
    line1.set_data(range(t), healthy_curve[:t])
    line2.set_data(range(t), infection_curve[:t])
    line3.set_data(range(t), recovery_curve[:t])
    line4.set_data(range(t), dead_curve[:t])
    line5.set_data(range(t), hos_curve[:t])
    line6.set_data(range(t), mhos_curve[:t])
    return line2, line3, line4, line5, line6

ani2 = animation.FuncAnimation(fig2, go, frames=100, interval=100, blit=True, repeat=False)
with open("test1_line.html", "w") as g:
    print(ani2.to_html5_video(), file=g)
