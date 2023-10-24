import os
import time
import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest, UpdateDomainRecordRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
import re
import json

def is_valid_ip(ip):
    return bool(re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip))

def get_public_ip():
    response = requests.get('http://members.3322.org/dyndns/getip')
    ip = response.text.strip()
    return ip if is_valid_ip(ip) else None

def get_ali_record_ip(client, domain_name, rr):
    try:
        request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        request.set_DomainName(domain_name)
        raw_response = client.do_action_with_exception(request)
        response = json.loads(raw_response.decode('utf-8'))
        records = response["DomainRecords"]["Record"]
        for record in records:
            if record["RR"] == rr:
                return record["Value"], record["RecordId"]
    except (ClientException, ServerException) as e:
        print(f"Exception while fetching Aliyun DNS record: {e}")
        return None, None

def update_dns(client, domain_name, rr, public_ip, record_id):
    try:
        request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        request.set_RecordId(record_id)
        request.set_RR(rr)
        request.set_Value(public_ip)
        request.set_Type("A")  # Set record type to "A"
        client.do_action_with_exception(request)
    except (ClientException, ServerException) as e:
        print(f"Exception while updating Aliyun DNS record: {e}")

if __name__ == "__main__":
    print("DDNS 更新脚本已开始运行...\n")

    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DOMAIN_NAME = os.getenv("DOMAIN_NAME")
    RR = os.getenv("RR")

    client = AcsClient(ACCESS_KEY, SECRET_KEY, "cn-hangzhou")
    previous_ip, record_id = get_ali_record_ip(client, DOMAIN_NAME, RR)
    updates_log = []

    while True:
        time.sleep(10)  # Sleep first to prevent immediate repetition

        os.system('clear')  # Clear terminal content
        print("DDNS 更新脚本已开始运行...\n")

        public_ip = get_public_ip()
        if not public_ip:
            continue

        print(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前IP: {public_ip}")
        print(f"记录IP: {previous_ip}\n")

        if public_ip != previous_ip:
            try:
                update_dns(client, DOMAIN_NAME, RR, public_ip, record_id)
                log_entry = f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 旧IP: {previous_ip}, 新IP: {public_ip}"
                updates_log.append(log_entry)
                if len(updates_log) > 5:  # Keep only the last 5 entries
                    updates_log.pop(0)
                previous_ip = public_ip  # Update the previous IP after updating
            except Exception as e:
                print(f"Exception during DNS update: {e}")

        print("\n".join(updates_log))
