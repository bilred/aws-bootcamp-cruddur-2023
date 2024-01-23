# Week 5 — DynamoDB and Serverless Caching
DynamoDB is a NoSQL database, based on key, value concepts.
A data modeling technique called single table design stores all relevant data in a single database table. For the Direct Messaging System in our Cruddur application, we use DynamoDB.

## Data Modeling principal
- Data duplication would be good if we have a use case in our application (specifically with data volume) unlike the relational database.
- To design our data structure we need to find our "Utilisation Patterns"
- Based on our utilization patterns, We can make decisions about what we need
  * Flat table (make essay the relation without joining but with duplication data)
  * Who is our P.K (Partition Key), S.K (Sort Key)
  * Design what the application does is important before starting (to extract the patterns)


## Access Patterns
Four patterns of data access can be distinguished in this context:
- use `Pattern A` for displaying messages. A list of messages that are a part of a message group are visible to users.
- use `Pattern B` for displaying message groups. Users can check the other people they have been communicating with by viewing a list of messaging groups.
- use `Pattern C` for composing a fresh message in a fresh message group.
- use `Pattern D` for adding a new message to an existing message group.
  

So, there are tree types of items to insert in our Dynamo DB Table:
```py
my_message_group = {
    'pk': {'S': f"GRP#{my_user_uuid}"},
    'sk': {'S': last_message_at},
    'message_group_uuid': {'S': message_group_uuid},
    'message': {'S': message},
    'user_uuid': {'S': other_user_uuid},
    'user_display_name': {'S': other_user_display_name},
    'user_handle':  {'S': other_user_handle}
}

other_message_group = {
    'pk': {'S': f"GRP#{other_user_uuid}"},
    'sk': {'S': last_message_at},
    'message_group_uuid': {'S': message_group_uuid},
    'message': {'S': message},
    'user_uuid': {'S': my_user_uuid},
    'user_display_name': {'S': my_user_display_name},
    'user_handle':  {'S': my_user_handle}
}

message = {
    'pk':   {'S': f"MSG#{message_group_uuid}"},
    'sk':   {'S': created_at},
    'message': {'S': message},
    'message_uuid': {'S': message_uuid},
    'user_uuid': {'S': my_user_uuid},
    'user_display_name': {'S': my_user_display_name},
    'user_handle': {'S': my_user_handle}
}
```

## Working of Backend 
We need map data in Postgres with data in Dynamodb using the Cognito_user_id using our seed.sql into db and ddb folder.

1- Insert the data `backend-flask/db/seed.sql` (we need to find cognito_user_id from aws) 
2- List users data saved in AWS Cognito, create the `backend-flask/bin/cognito/list-users` (using boto3 - client aws for python)
3- To update users in the (db) seed data with actual Cognito IDs, create the `backend-flask/bin/db/update_cognito_user_ids`
4- Then we also added a conversation (messages) between 'Person1' and a user handle named 'Person1' in a file `bin/ddb/seed.sql` (make sure that working accordingly with data seed in postgrs db local). (time zone is important)


**Here is the result of how it looks after loading the messages and adding my message to that group.**
![](https://user-images.githubusercontent.com/115455157/231931460-f1bee3fc-d39c-4966-875e-e2f93e6fea95.png)

## Lambda cruddur-messaging-stream
Trigger the action (Delete and Create) in DynamoDB when updating the message groups via Lambda `aws/lambdas/cruddur-messaging-stream.py`

required for :
- create a VPC endpoint for dynamoDB service on your VPC
- create a Python lambda function in your vpc
- enable streams on the table with 'new image' attributes included
- add your function as a trigger on the stream
- grant the lambda IAM role permission to read the DynamoDB stream events

`AWSLambdaInvocation-DynamoDB`

- grant the lambda IAM role permission to update table items


**The Function**
```py
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource(
 'dynamodb',
 region_name='ca-central-1',
 endpoint_url="http://dynamodb.ca-central-1.amazonaws.com"
)

def lambda_handler(event, context):
  print('event-data',event)

  eventName = event['Records'][0]['eventName']
  if (eventName == 'REMOVE'):
    print("skip REMOVE event")
    return
  pk = event['Records'][0]['dynamodb']['Keys']['pk']['S']
  sk = event['Records'][0]['dynamodb']['Keys']['sk']['S']
  if pk.startswith('MSG#'):
    group_uuid = pk.replace("MSG#","")
    message = event['Records'][0]['dynamodb']['NewImage']['message']['S']
    print("GRUP ===>",group_uuid,message)

    table_name = 'cruddur-messages'
    index_name = 'message-group-sk-index'
    table = dynamodb.Table(table_name)
    data = table.query(
      IndexName=index_name,
      KeyConditionExpression=Key('message_group_uuid').eq(group_uuid)
    )
    print("RESP ===>",data['Items'])

    # recreate the message group rows with new SK value
    for i in data['Items']:
      delete_item = table.delete_item(Key={'pk': i['pk'], 'sk': i['sk']})
      print("DELETE ===>",delete_item)

      response = table.put_item(
        Item={
          'pk': i['pk'],
          'sk': sk,
          'message_group_uuid':i['message_group_uuid'],
          'message':message,
          'user_display_name': i['user_display_name'],
          'user_handle': i['user_handle'],
          'user_uuid': i['user_uuid']
        }
      )
      print("CREATE ===>",response)
```

-------------------------------------------------------
-------------------------------------------------------
## Note1: DynamoDB Bash Scripts
```sh
./bin/ddb/schem-load
```
## Note2: The Boundaries of DynamoDB
- When you write a query you have provide a Primary Key (equality) eg. pk = 'andrew'
- Are you allowed to "update" the Hash and Range?
    - No, whenever you change a key (simple or composite) eg. pk or sk you have to create a new item.
    - you have to delete the old one
- Key condition expressions for query only for RANGE, HASH is only equality 
- Don't create UUID for entity if you don't have an access pattern for it
