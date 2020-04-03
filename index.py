import time
import json
import os
import ast
import boto3

from botocore.exceptions import ClientError

client = boto3.client('ses')


def handler(event):
    message = event['Records'][0]['Sns']['Message']
    print("SNS Notifications: " + message)

    json_dict = json.loads(message)
    email_id = json_dict['Email']['StringValue']
    print(json_dict['Email']['StringValue'])

    domain = os.environ['domain']
    sender = "no-reply@" + domain
    print("Email Sender: " + sender)

    to = "nishanth.di.m@gmail.com"

    bills_list = json_dict['Bills']['StringValue']
    bills = ast.literal_eval(bills_list)

    email_body = ""
    for i in range(0, len(bills)):
        email_body += "<bill>" + "http://" + domain + "/v1/bill/" + bills[i]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('csye6225DynamoDB')

    seconds = 10
    ttl = int(time.time()) + seconds

    try:
        response = table.get_item(
            Key={
                'email': email_id
            })

        if 'Item' not in response:
            response = table.put_item(
                Item={
                    'email': email_id,
                    'TTL': ttl
                })

            response = client.send_email(
                Destination={
                    'ToAddresses': [to],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': email_body,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': 'List of your Due Bills',
                    },
                },
                Source=sender,
            )

    except ClientError as error:
        print(error.response['Error']['Message'])

    return message
