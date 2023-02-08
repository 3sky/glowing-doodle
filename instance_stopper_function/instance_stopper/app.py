import boto3

from model.aws.ec2 import Marshaller
from model.aws.ec2 import AWSEvent
from model.aws.ec2 import EC2InstanceStateChangeNotification


def lambda_handler(event, context):

    # Deserialize event into strongly typed object
    awsEvent, ec2StateChangeNotification = deserialize_event(event)

    # use boto3 as client
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(ec2StateChangeNotification.instance_id)
    tags: dict = instance.tags

    # Execute business logic
    if search_owner(tags) is None:
        print("Kill it: " + ec2StateChangeNotification.instance_id)
        # Termiante instance with Owner tag
        instance.terminate()

        # Make updates to event payload
        awsEvent.detail_type = "Lambda function terminated the machine " + ec2StateChangeNotification.instance_id + " " + awsEvent.detail_type

    # Return event for further processing
    return Marshaller.marshall(awsEvent)


def search_owner(tags):

    if (next((x for x in tags if x["Key"] == "Owner"), None)) is None:
        return None
    else:
        return "Owner exist"


def deserialize_event(event):

    awsEvent: AWSEvent = Marshaller.unmarshall(event, AWSEvent)
    ec2StateChangeNotification: EC2InstanceStateChangeNotification = awsEvent.detail

    print("Region is " + awsEvent.region)
    print("Instance " + ec2StateChangeNotification.instance_id + " transitioned to " + ec2StateChangeNotification.state)

    return awsEvent, ec2StateChangeNotification
