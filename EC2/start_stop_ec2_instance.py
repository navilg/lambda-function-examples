#!/usr/bin/env python3
import os
import boto3

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
    for instance in instances_to_start:
        instance.start()
        instance_state_changed += 1
    return instance_state_changed

def stop_ec2_instance(region,filter_tag_key="",filter_tag_value=""):
    instances_to_stop = list_ec2_instance(region,filter_tag_key,filter_tag_value,state='running')
    instance_state_changed = 0
    for instance in instances_to_stop:
        instance.stop()
        instance_state_changed += 1
    return instance_state_changed

def lambda_handler(event,context):
    #region = os.getenv('REGION','ap-south-1')
    region = event.get('region')
    action = os.getenv('ACTION','list')
    filter_tag_key = event.get('filter_tag_key')
    filter_tag_value = event.get('filter_tag_value')

    instance_status_change = 0
    if(event.get('action') == 'start'):
        instance_status_change = start_ec2_instance(region,filter_tag_key,filter_tag_value)
    elif(event.get('action') == 'stop'):
        instance_status_change = stop_ec2_instance(region,filter_tag_key,filter_tag_value)
    else:
        instance_status_change = list_ec2_instance(region)

    return instance_status_change


