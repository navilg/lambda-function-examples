import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event,context):

    region = event.get('region')
    subject = 'EC2 Stopped - AWS Protonmail'
    body = "EC2 instances has been stopped"

    client = boto3.client(service_name = 'ses', region_name = region)
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = "username@example.com"
    message['To'] = "tousername@example.com"

    # Message body

    content = MIMEText(body, 'html')
    message.attach(content)

    destination = { 'ToAddresses' : [message['To']], 'CcAddresses' : [], 'BccAddresses' : []}

    client.send_raw_email(Source = message['From'], Destinations = [message['To']], RawMessage = {'Data': message.as_string(),})
    return 1
