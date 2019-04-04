# autocar

[感谢zhengwang的这篇博客](https://zhengludwig.wordpress.com/projects/self-driving-rc-car/)

[原作者github链接](https://github.com/hamuchiwa/AutoRCCar)
## Pytho3 + opencv3
此项目是在zhengwang的基础下进行修改的，树莓派改用性能更强大的linux主机，<br>
pi_camera改用为普通的webcam，底层采用stm32进行小车的控制，小车选择的1/14的RC遥控车进行改装，<br>
电机驱动采用tb6612，转向由舵机进行控制,所有程序运行均在linux主机上。

## 搭建linux环境

这里采用ubuntu作为案例，首先需要将系统更新为最新状态

		sudo apt update && apt upgrade

接下来安装opencv3到python3上,步骤比较繁琐：

	1.Install CMAKE developer packages(安装cmake包)

		sudo apt-get install build-essential cmake pkg-config -y
		
	2.Install Image I/O packages（安装图像io包）

		sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev -y
	
	3.Install Video I/O packages（安装视频io包）

		sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
		sudo apt-get install libxvidcore-dev libx264-dev -y
	
	4.Install the GTK development library for basic GUI windows（安装GTK开发包）
		
		sudo apt-get install libgtk2.0-dev libgtk-3-dev -y

	5.Install optimization packages (improved matrix operations for OpenCV)
		（安装矩阵改进包，可安装可不）
		sudo apt-get install libatlas-base-dev gfortran -y

	6.Install Python 3 and numpy（安装python3和numpy）

		sudo apt-get install python3 python3-setuptools python3-dev -y
		wget https://bootstrap.pypa.io/get-pip.py
		sudo python3 get-pip.py
		sudo pip3 install numpy
	
	7.下载opencv3.4和opencv3.4扩展包（版本一定要对应）

		cd ~
		wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.0.zip
		unzip opencv.zip
		wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.0.zip
		unzip opencv_contrib.zip

	7.Compile and Install OpenCV 3.4.0 for Python 3（cmake）
		
		cd opencv-3.4.0
		mkdir build
		cd build
		cmake -D CMAKE_BUILD_TYPE=RELEASE \
		-D CMAKE_INSTALL_PREFIX=/usr/local \
		-D BUILD_opencv_java=OFF \
		-D BUILD_opencv_python2=OFF \
		-D BUILD_opencv_python3=ON \
		-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
		-D INSTALL_C_EXAMPLES=OFF \
		-D INSTALL_PYTHON_EXAMPLES=ON \
		-D BUILD_EXAMPLES=ON\
		-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.0/modules \
		-D WITH_CUDA=OFF \
		-D BUILD_TESTS=OFF \
		-D BUILD_PERF_TESTS= OFF ..

	8.Finally Ready to be Compile（编译）
		
		make -j4

	9.Install the build （安装）
	
		sudo make install
		sudo ldconfig

	10.Verify the OpenCV build（验证）
	
		python3
		import cv2
		print(cv2.__version__)


-----------------------------------
## 安装pygame，sklearn等(sklearn版本要大于0.18)

		pip3 install pygame
		
  安装的sklearn版本要是小于0.18，可以用下面的指令升级
  
  		pip3 install -U scikit-learn


## 源码编译安装pygame

	安装pygame依赖环境
		sudo apt-get build-dep python-pygame
		sudo apt-get install mercurial python3-dev python3-numpy libav-tools \
		libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
		libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
	下载源码
		hg clone https://bitbucket.org/pygame/pygame
		cd pygame
		python3 setup.py build
		sudo python3 setup.py install

## 解决opencv和ros的文件冲突

		import sys
		ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
		if ros_path in sys.path:
			sys.path.remove(ros_path)
		import cv2
		sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')

## 解决ubuntu的串口权限问题

	查看当前用户名
		~$ whoami
		   dj40
		~$ sudo usermod -aG dialout dj140

--------------------------------
## 简单操作

		./driver.py (单纯控制小车前后左右)
		./collectdata.py (打开摄像头，采集数据，键盘每按下一次即记录图片信息)
		./model_training.py (导入数据，训练模型)
		./auto_driver.py (自动驾驶)


