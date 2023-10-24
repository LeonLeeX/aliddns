# ALIYUN DDNS

自动更新公网IP域名记录。

## 描述

自动检测并更新公网IP地址到阿里云DDNS记录。

## Docker 部署

### 使用 `docker run` 运行

1. 从 Docker Hub 获取最新的镜像。
```bash
docker pull lenlee/aliddns:lasted
```
运行容器。根据实际情况设置下面的环境变量。
```bash
docker run -e ACCESS_KEY=你的阿里云ACCESS_KEY -e SECRET_KEY=你的阿里云SECRET_KEY -e DOMAIN_NAME=你的域名 -e RR=二级域名记录 lenlee/aliddns:lasted
```
### 使用 `docker-compose` 运行
创建一个 docker-compose.yml 文件并添加以下内容：
```yml
version: '3'
services:
  aliddns:
    image: lenlee/aliddns:lasted
    environment:
      - ACCESS_KEY=你的阿里云ACCESS_KEY
      - SECRET_KEY=你的阿里云SECRET_KEY
      - DOMAIN_NAME=你的域名
      - RR=二级域名记录
```
使用 docker-compose 启动容器。
```bash
docker-compose up -d
```
请确保替换“你的阿里云ACCESS_KEY”、“你的阿里云SECRET_KEY”、“你的域名”和“二级域名记录”为实际值。