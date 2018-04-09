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
