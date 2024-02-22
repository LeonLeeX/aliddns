import os
import time
import requests
import re
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest, UpdateDomainRecordRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException

def is_valid_ip(ip):
    return bool(re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip))

def get_public_ip():
    try:
        response = requests.get('http://members.3322.org/dyndns/getip')
        ip = response.text.strip()
        return ip if is_valid_ip(ip) else None
    except requests.RequestException:
        return None

def get_ali_record_ip(client, domain_name, rr):
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_DomainName(domain_name)
    raw_response = client.do_action_with_exception(request)
    response = json.loads(raw_response.decode('utf-8'))
    records = response["DomainRecords"]["Record"]
    for record in records:
        if record["RR"] == rr:
            return record["Value"], record["RecordId"]
    return None, None

def update_dns(client, domain_name, rr, public_ip, record_id):
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_RecordId(record_id)
    request.set_RR(rr)
    request.set_Value(public_ip)
    request.set_Type("A")  # Set record type to "A"
    client.do_action_with_exception(request)

def reinitialize_client(access_key, secret_key):
    return AcsClient(access_key, secret_key, "cn-hangzhou")

if __name__ == "__main__":
    print("DDNS 更新脚本已开始运行...\n")

    # 环境变量
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DOMAIN_NAME = os.getenv("DOMAIN_NAME")
    # 支持多个RR值，用逗号分隔
    RRs = os.getenv("RR").split(',')

    # 初始化
    client = AcsClient(ACCESS_KEY, SECRET_KEY, "cn-hangzhou")
    updates_log = []
    previous_ips = {}

    while True:
        time.sleep(10)  # 每次循环的睡眠时间
        public_ip = get_public_ip()
        if not public_ip:
            continue

        for RR in RRs:
            try:
                current_ip, record_id = get_ali_record_ip(client, DOMAIN_NAME, RR)
                if not current_ip:
                    raise Exception("无法获取阿里云DNS记录")

                if public_ip != previous_ips.get(RR):
                    update_dns(client, DOMAIN_NAME, RR, public_ip, record_id)
                    log_entry = f"更新[{RR}] 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 旧IP: {previous_ips.get(RR, '无')}, 新IP: {public_ip}"
                    updates_log.append(log_entry)
                    if len(updates_log) > 5:
                        updates_log.pop(0)
                    previous_ips[RR] = public_ip

            except (ClientException, ServerException, Exception) as e:
                print(f"[{RR}] 异常发生，重新初始化 AcsClient: {e}")
                client = reinitialize_client(ACCESS_KEY, SECRET_KEY)
                continue

        print("\n".join(updates_log))