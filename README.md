# w9-demo

#### 介绍
w9-demo是9周大实训的一个演示程序，主要为了展示如何在Vue前端和Flask后端之间建立数据访问机制。
1、Vue前端开发时可以用nodejs进行管理，发布时需要build，然后把静态页面部署到nginx或者其他www服务器中。
2、Flask后端则直接用run-back.py启动

#### 软件架构
前端用Vue构建界面，后端用Flask微服务结构，数据存储不限制，可以是mongoDB或者mysql或者Redis

#### 使用说明

1.  前端启动: 可以用run-front.py脚本启动，也可以用npm run dev启动
2.  后端启动：可以用run-back.py脚本启动