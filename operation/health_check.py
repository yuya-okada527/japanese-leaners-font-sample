import os
import urllib.request
from urllib.error import URLError

import boto3


def lambda_handler(event, context):
    # ヘルスチェック
    url = os.getenv("APP_HEALTH_END_POINT")
    req = urllib.request.Request(url)
    try:
        res = urllib.request.urlopen(req)
        status = res.getcode()
        if status == 200:
            return "OK"
    except URLError as e:
        # 失敗の場合メール通知
        pass

    # メール通知
    client = boto3.client('ses',
                          aws_access_key_id=os.getenv("SES_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv("SES_SECRET_KEY"),
                          region_name=os.getenv("REGION")
                          )

    client.send_email(
        Source=os.getenv("SOURCE_MAIL_ADDRESS"),
        Destination={
            'ToAddresses': [
                os.getenv("TO_MAIL_ADDRESS"),
            ]
        },
        Message={
            'Subject': {
                'Data': '[警告] JCW-DEMO-APPクラッシュ',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': 'JCW-DEMO-APPのヘルスチェックに失敗しました。URL: ' + url,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    return "NG"
