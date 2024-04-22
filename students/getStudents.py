import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

def get_students(dynamodb_table):
    try:
        scan_params = {
            'TableName': dynamodb_table.name
        }
        return build_response(200, scan_dynamo_records(scan_params, [],dynamodb_table))
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def scan_dynamo_records(scan_params, item_array,dynamodb_table):
    response = dynamodb_table.scan(**scan_params)
    item_array.extend(response.get('Items', []))
   
    if 'LastEvaluatedKey' in response:
        scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
        return scan_dynamo_records(scan_params, item_array)
    else:
        return {'students': item_array}
    
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