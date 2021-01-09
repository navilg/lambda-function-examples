import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

'''
# event JSON example

To start the instance
{"action": "start", "region": "eu-north-1", "filter_tag_key": "auto_start", "filter_tag_value": "y"}

To stop the instance
{"action": "stop", "region": "eu-north-1", "filter_tag_key": "auto_stop", "filter_tag_value": "y"}
'''

def list_ec2_instance(region,filter_tag_key,filter_tag_value,state='all'):
    ec2_instances = []

    ec2_obj = boto3.resource('ec2',region_name=region)
    if(state == 'running'):
        filters = [{'Name': 'instance-state-name','Values': [state]},{'Name': 'tag:'+filter_tag_key,'Values': [filter_tag_value]}]
    elif(state == 'stopped'):
        filters = [{'Name': 'instance-state-name','Values': [state]},{'Name': 'tag:'+filter_tag_key,'Values': [filter_tag_value]}]
    else:
        filters = []

    for instance in ec2_obj.instances.filter(Filters=filters):
        ip = instance.private_ip_address
        state_name = instance.state['Name']
        print("ip:{}, state:{}".format(ip,state_name))
        ec2_instances.append(instance)

    return ec2_instances

def start_ec2_instance(region,filter_tag_key="",filter_tag_value=""):
    instances_to_start = list_ec2_instance(region,filter_tag_key,filter_tag_value,state='stopped')
    instance_state_changed = 0
    print("Starting")
    print(instances_to_start)
    for instance in instances_to_start:
        instance.start()
        instance_state_changed += 1
    return instance_state_changed

def stop_ec2_instance(region,filter_tag_key="",filter_tag_value=""):
    instances_to_stop = list_ec2_instance(region,filter_tag_key,filter_tag_value,state='running')
    instance_state_changed = 0
    print("Stopping")
    print(instances_to_stop)
    for instance in instances_to_stop:
        instance.stop()
        instance_state_changed += 1
    return instance_state_changed

def send_mail_ses(region,fromaddr,toaddr,subject,body):
    client = boto3.client(service_name = 'ses', region_name = region)
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = fromaddr
    message['To'] = toaddr
    print("Sending mail to ",message['To'])
    # Message body

    content = MIMEText(body, 'html')
    message.attach(content)

    destination = { 'ToAddresses' : [message['To']], 'CcAddresses' : [], 'BccAddresses' : []}

    client.send_raw_email(Source = message['From'], Destinations = [message['To']], RawMessage = {'Data': message.as_string(),})


def lambda_handler(event,context):
    #region = os.getenv('REGION','ap-south-1')
    region = event.get('region')
    action = os.getenv('ACTION','list')
    filter_tag_key = event.get('filter_tag_key')
    filter_tag_value = event.get('filter_tag_value')
    fromaddr = "navilg0409@gmail.com"
    toaddr = "navilg0409@gmail.com"

    instance_status_change = 0
    if(event.get('action') == 'start'):
        instance_status_change = start_ec2_instance(region,filter_tag_key,filter_tag_value)
        if(instance_status_change > 0):
            subject = "EC2 instance started"
            body = str(instance_status_change)+" instance/s started in "+str(region)
            send_mail_ses(region,fromaddr,toaddr,subject,body)
    elif(event.get('action') == 'stop'):
        instance_status_change = stop_ec2_instance(region,filter_tag_key,filter_tag_value)
        if(instance_status_change > 0):
            subject = "EC2 instance stopped"
            body = str(instance_status_change)+" instance/s stopped in "+str(region)
            send_mail_ses(region,fromaddr,toaddr,subject,body)
    else:
        instance_status_change = list_ec2_instance(region)

    return instance_status_change
    
