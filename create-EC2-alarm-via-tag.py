import boto3
import os
import cfnresponse


def create_alarm_for_instance(cloudwatch, instance_id, sns_topic):
    try:
        cloudwatch.put_metric_alarm(
            AlarmName=f'{os.environ["METRIC_NAME"]}-{instance_id}',
            AlarmDescription=f'{os.environ["METRIC_NAME"]} alarm for EC2 instance {instance_id}',
            MetricName=os.environ['METRIC_NAME'],
            Namespace='AWS/EC2',
            Statistic=os.environ['STATISTIC'],
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            Period=int(os.environ['PERIOD']),
            EvaluationPeriods=int(os.environ['EVALUATION_PERIODS']),
            DatapointsToAlarm=int(os.environ['DATAPOINTS_TO_ALARM']),
            Threshold=float(os.environ['THRESHOLD']),
            ComparisonOperator=os.environ['COMPARISON_OPERATOR'],
            AlarmActions=[sns_topic]
        )
        print(f"Created alarm for instance {instance_id}")
        return True
    except Exception as e:
        print(f"Error creating alarm for instance {instance_id}: {str(e)}")
        return False


def delete_alarm_for_instance(cloudwatch, instance_id):
    try:
        cloudwatch.delete_alarms(
            AlarmNames=[f'{os.environ["METRIC_NAME"]}-{instance_id}']
        )
        print(f"Deleted alarm for instance {instance_id}")
        return True
    except Exception as e:
        print(f"Error deleting alarm for instance {instance_id}: {str(e)}")
        return False


def get_tagged_instances():
    ec2 = boto3.client('ec2')
    paginator = ec2.get_paginator('describe_instances')
    instances = []

    tag_key = os.environ['TAG_KEY']
    tag_value = os.environ['TAG_VALUE']

    try:
        for page in paginator.paginate(
                Filters=[
                    {
                        'Name': f'tag:{tag_key}',
                        'Values': [tag_value]
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': ['running', 'pending']
                    }
                ]
        ):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(instance['InstanceId'])
        return instances
    except Exception as e:
        print(f"Error getting tagged instances: {str(e)}")
        return []


def lambda_handler(event, context):
    if 'RequestType' in event:
        try:
            cloudwatch = boto3.client('cloudwatch')
            sns_topic = os.environ['SNS_TOPIC_ARN']

            if event['RequestType'] in ['Create', 'Update']:
                instances = get_tagged_instances()
                for instance_id in instances:
                    create_alarm_for_instance(cloudwatch, instance_id, sns_topic)

                cfnresponse.send(event, context, cfnresponse.SUCCESS, {
                    'InstanceCount': len(instances)
                })

            elif event['RequestType'] == 'Delete':
                instances = get_tagged_instances()
                for instance_id in instances:
                    delete_alarm_for_instance(cloudwatch, instance_id)

                cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

        except Exception as e:
            print(f"Error in custom resource handler: {str(e)}")
            cfnresponse.send(event, context, cfnresponse.FAILED, {})

        return

    # 处理 EC2 实例状态变化事件
    if 'detail' in event and 'instance-id' in event['detail']:
        instance_id = event['detail']['instance-id']
        state = event['detail']['state']

        ec2 = boto3.client('ec2')
        response = ec2.describe_instances(InstanceIds=[instance_id])

        # 检查实例是否有匹配的标签
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                tags = instance.get('Tags', [])
                for tag in tags:
                    if (tag['Key'] == os.environ['TAG_KEY'] and
                            tag['Value'] == os.environ['TAG_VALUE']):

                        cloudwatch = boto3.client('cloudwatch')
                        if state == 'running':
                            create_alarm_for_instance(
                                cloudwatch,
                                instance_id,
                                os.environ['SNS_TOPIC_ARN']
                            )
                        elif state in ['terminated', 'stopped']:
                            delete_alarm_for_instance(cloudwatch, instance_id)

    return {
        'statusCode': 200,
        'body': 'Processing completed'
    }