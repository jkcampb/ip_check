from influxdb import InfluxDBClient
from twilio.rest import Client

import os
from requests import get
import time


class InfluxClient:
    def __init__(self, ip_address, ip_changed):
        influx_host = os.environ["INFLUX_HOST"]
        influx_port = os.environ["INFLUX_PORT"]
        influx_user = os.environ["INFLUX_USER"]
        influx_pass = os.environ["INFLUX_PASSWORD"]
        
        self.client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, 'ipcheck')
        self.ip_address = ip_address
        self.ip_changed = int(ip_changed)


    def write(self):
        ip_data = [
            {
            "measurement" : "ip_check",
            "tags" : {
            "host": "RaspberryPi"
            },
                "fields" : {
                "ip":self.ip_address,
                "ip_change": self.ip_changed
                }
            }
        ]

        self.client.write_points(ip_data)


class TwilioClient:
    def __init__(self, ip_address):
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']
        self.auth_token = os.environ['TWILIO_ACCOUNT_AUTH_TOKEN']
        self.from_sms = os.environ['TWILIO_FROM_SMS']
        self.to_sms = os.environ['TWILIO_TO_SMS']

        self.new_ip = ip_address
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def notify(self):
        self.client.messages.create(
            body=f"Home IP Address is now {self.new_ip}",
            from_=self.from_sms,
            to=self.to_sms
        )


def main(record_client=InfluxClient, notify_client=TwilioClient):

    ip = get('https://api.ipify.org').text

    try:
        with open('./current_ip', 'r') as reader:
            last_ip = reader.readline()
    except FileNotFoundError:
        last_ip = ''


    ip_changed = ((last_ip!=ip) & (last_ip != ''))
    
    if ip_changed:
        with open('./current_ip', 'w+') as writer:
            writer.write(ip)

        notify_client.notify(ip)


    record_client(ip, ip_changed).write()


if __name__ == '__main__':
    main()
