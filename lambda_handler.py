import json
import csv
import boto3

# Initialize AWS services
s3_client = boto3.client('s3')
connect_client = boto3.client('connect')

instance_id =  "1a60da9e-2e91-47ec-980a-29b437893c21"
routing_profile_id = "9f97c09b-1acd-4517-9084-be028242e392"


def lambda_handler(event, context):
    # Get the S3 bucket and object key from the S3 event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    
    # Download the CSV file from S3
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    csv_data = response['Body'].read().decode('utf-8').splitlines()


# create,"lester","password456","9f97c09b-1acd-4517-9084-be028242e392", "1a60da9e-2e91-47ec-980a-29b437893c21"
    
    for row in csv.reader(csv_data):
        # Use strip() to remove white spaces from each value
        cleaned_row = [value.strip(' "\'') for value in row if value.strip(' "\'')]

        if len(cleaned_row) != 5:
            print("Invalid number of values in row.")
            continue

        action, username, password, routing_profile_id, instance_id = cleaned_row

        if action == 'create':
            create_connect_user(username, password, routing_profile_id, instance_id)
        elif action == 'delete':
            # delete_connect_user(user_id, instance_id)
            pass
        else:
            print(f"Invalid action: {action}")

def create_connect_user(username, password, routing_profile_id=routing_profile_id, instance_id=instance_id):
    try:
        response = connect_client.create_user(
            Username=username,
            Password=password,
            IdentityInfo={
                'FirstName': username,  
                'LastName': 'User',    
            },
            PhoneConfig={
                'PhoneType': 'SOFT_PHONE',
            },
            SecurityProfileIds=[routing_profile_id],
            RoutingProfileId=routing_profile_id,
            InstanceId=instance_id
        )
        print(f"User {username} created with ID: {response['UserId']}")
    except Exception as e:
        print(f"Error creating user: {str(e)}")

def delete_connect_user(user_id, instance_id):
    try:
        response = connect_client.delete_user(
            InstanceId=instance_id,
            UserId=user_id
        )
        print(f"User {user_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting user: {str(e)}")


#creating and deleting a user requires corresponding ID key for the resource 
#aws connect list-instances
#aws connect list-users --instance_id

# create_connect_user("jubei","Passw0rd!",routing_profile_id, instance_id)
# delete_connect_user(user_id="cbefd263-154f-4ee8-ade2-85cc2d2d79ad",instance_id=instance_id)

#format of csv
# Action,Username,Password,RoutingProfileId,InstanceId
# create,user1,password123,profile-id-1,instance-id-1,
# create,user2,password456,profile-id-2,instance-id-1,
# delete,user3,,profile-id-3,instance-id-1
#  aws connect list-users --instance-id "1a60da9e-2e91-47ec-980a-29b437893c21"

# {
#     "UserSummaryList": [
#         {
#             "Id": "481e35d8-68a1-4f0b-898d-fe88ea549179",
#             "Arn": "arn:aws:connect:us-east-1:3325:instance/1/agent/481e35d8-fe88ea549179",
#             "Username": "thecloudshepherd"
#         }
#     ]
# }
