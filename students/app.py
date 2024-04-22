import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Key

from getStudents import get_students
from getStudent import get_student
from saveStudent import save_student
from modifyStudent import modify_student
from deleteStudent import delete_student

# Initialize the DynamoDB client using boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
dynamodb_table = dynamodb.Table('student_info')

status_check_path = '/status'
student_path = '/student'
students_path = '/students'

def lambda_handler(event, context):
    print('Request event: ', event)
    response = None
   
    try:
        http_method = event.get('httpMethod')
        path = event.get('path')

        if http_method == 'GET' and path == status_check_path:
            response = build_response(200, 'Service is operational')
        elif http_method == 'GET' and path == student_path:
            student_id = event['queryStringParameters']['studentid']
            response = get_student(student_id,dynamodb_table)
        elif http_method == 'GET' and path == students_path:
            response = get_students(dynamodb_table)
        elif http_method == 'POST' and path == student_path:
            response = save_student(json.loads(event['body']),dynamodb_table)
        elif http_method == 'PATCH' and path == student_path:
            body = json.loads(event['body'])
            response = modify_student(body['studentId'], body['updateKey'], body['updateValue'],dynamodb_table)
        elif http_method == 'DELETE' and path == student_path:
            body = json.loads(event['body'])
            response = delete_student(body['studentId'],dynamodb_table)
        else:
            response = build_response(404, '404 Not Found')

    except Exception as e:
        print('Error:', e)
        response = build_response(400, 'Error processing request')
   
    return response

# def get_student(student_id):
#     try:
#         response = dynamodb_table.get_item(Key={'studentid': student_id})
#         return build_response(200, response.get('Item'))
#     except ClientError as e:
#         print('Error:', e)
#         return build_response(400, e.response['Error']['Message'])

# def get_students():
#     try:
#         scan_params = {
#             'TableName': dynamodb_table.name
#         }
#         return build_response(200, scan_dynamo_records(scan_params, []))
#     except ClientError as e:
#         print('Error:', e)
#         return build_response(400, e.response['Error']['Message'])

# def scan_dynamo_records(scan_params, item_array):
#     response = dynamodb_table.scan(**scan_params)
#     item_array.extend(response.get('Items', []))
   
#     if 'LastEvaluatedKey' in response:
#         scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
#         return scan_dynamo_records(scan_params, item_array)
#     else:
#         return {'students': item_array}

# def save_student(request_body):
#     try:
#         dynamodb_table.put_item(Item=request_body)
#         body = {
#             'Operation': 'SAVE',
#             'Message': 'SUCCESS',
#             'Item': request_body
#         }
#         return build_response(200, body)
#     except ClientError as e:
#         print('Error:', e)
#         return build_response(400, e.response['Error']['Message'])

# def modify_student(student_id, update_key, update_value):
#     try:
#         response = dynamodb_table.update_item(
#             Key={'studentid': student_id},
#             UpdateExpression=f'SET {update_key} = :value',
#             ExpressionAttributeValues={':value': update_value},
#             ReturnValues='UPDATED_NEW'
#         )
#         body = {
#             'Operation': 'UPDATE',
#             'Message': 'SUCCESS',
#             'UpdatedAttributes': response
#         }
#         return build_response(200, body)
#     except ClientError as e:
#         print('Error:', e)
#         return build_response(400, e.response['Error']['Message'])

# def delete_student(student_id):
#     try:
#         response = dynamodb_table.delete_item(
#             Key={'studentid': student_id},
#             ReturnValues='ALL_OLD'
#         )
#         body = {
#             'Operation': 'DELETE',
#             'Message': 'SUCCESS',
#             'Item': response
#         }
#         return build_response(200, body)
#     except ClientError as e:
#         print('Error:', e)
#         return build_response(400, e.response['Error']['Message'])

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Check if it's an int or a float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }