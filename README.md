### 是什么

是2018华为软件精英挑战赛，虚拟机销量预测的本地打分程序，由原作者folk而来并做了大量改进。

### 使用方法

Copy your `predictor.py` to this dir.
Then run:

    $ ./one.sh

GET YOUR SCORE!

---

修复的几个问题：

- train和input文件与官方不符，进行了修改
- out中\r\n和\n的不同 （官方判题没有区别）
- 调用predictor 打印信息太多 进行了重定向 到 ecs_log

---

修改的几个地方：

- 增加了最后的输出信息
- 多进程调用程序，提高速度

经过使用

	time bash one.sh

测试，一次test用时由3min降为1min
