FROM python:3.12-slim

WORKDIR /app

COPY update_dns.py .


# 声明环境变量
ENV ACCESS_KEY=""
ENV SECRET_KEY=""
ENV DOMAIN_NAME=""
ENV RR=""
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install requests aliyun-python-sdk-core aliyun-python-sdk-alidns

CMD ["python", "-u", "./update_dns.py"]
