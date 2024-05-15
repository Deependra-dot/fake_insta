import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.resource("dynamodb")
s3 = boto3.client('s3')


def handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    bucket_name = os.environ.get("S3_BUCKET")
    logging.info(f"## Loaded table name from environemt variable DDB_TABLE: {table_name}")

    if event["httpMethod"] == "POST":
        return upload_image(event, table_name, bucket_name)
    elif event["httpMethod"] == "GET":
        return list_images(event, table_name, bucket_name)
    elif event["httpMethod"] == "DELETE":
        return delete_image(event, table_name, bucket_name)
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Invalid HTTP Method or missing parameters"}),
        }

def upload_image(event, table_name, bucket_name):
    table = dynamodb_client.Table(table_name)
    http_verb = event['httpMethod']
    unique_id = str(uuid.uuid4())
    if event["body"]:
        item = json.loads(event["body"])
        if "image" in item and "metadata" in item:
            image = item["image"]
            metadata = item["metadata"]
            print(type(image))
            print(type(metadata))
            print(http_verb)
            if image:
                s3.put_object(Bucket=bucket_name, Key=unique_id+".txt", Body=image)
                table.put_item(
                    Item={"id": unique_id, "metadata" :metadata},
                )
                message = "Successfully uploaded and inserted data!"
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"message": message}),
                }
            else:
                return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Image payload is not valid!"}),
        }
        else:
            return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Please Make sure image and metadata information is passed along with the payload!"}),
        }
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Please pass the right payload!"}),
        }

def list_images(event, table_name, bucket_name):

    table = dynamodb_client.Table(table_name)
    if event["queryStringParameters"] is None:
        # If 'queryStringParameters' is not present or is None, set filters to None
        dummy_filter1 = None
        dummy_filter2 = None
    elif "queryStringParameters" in event and "image_id" in event["queryStringParameters"]:
        return view_image(event, bucket_name)
    elif 'queryStringParameters' in event and ("filter1" in event["queryStringParameters"] or "filter2" in event["queryStringParameters"]):
        dummy_filter1 =event['queryStringParameters'].get("filter1")
        dummy_filter2 = event['queryStringParameters'].get("filter2")

    # Build the ExpressionAttributeValues for filtering
    filter_expression = {}
    if dummy_filter1:
        filter_expression[":dummy1"] = dummy_filter1
    if dummy_filter2:
        filter_expression[":dummy2"] = dummy_filter2

    # Construct the FilterExpression
    filter_expression_str = None
    if dummy_filter1 and dummy_filter2:
        filter_expression_str = "#metadata.test1 = :dummy1 AND #metadata.test2 = :dummy2"
    elif dummy_filter1:
        filter_expression_str = "#metadata.test1 = :dummy1"
    elif dummy_filter2:
        filter_expression_str = "#metadata.test2 = :dummy2"

    expression_attribute_names = {"#metadata": "metadata"}

    # Perform the scan with the filter expression
    if filter_expression_str:
        response = table.scan(
            FilterExpression=filter_expression_str,
            ExpressionAttributeValues=filter_expression,
            ExpressionAttributeNames= expression_attribute_names
        )
    else:
        response = table.scan()

    items = response.get('Items', [])
    if len(items)>0:
        items = [item["id"] for item in items]

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"images": items}),
    }

def view_image(event, bucket_name):
    if "queryStringParameters" in event and "image_id" in event["queryStringParameters"]:
        image_id = event["queryStringParameters"]["image_id"]
        try:
            response = s3.get_object(Bucket=bucket_name, Key=image_id + ".txt")
            image_data = response["Body"].read()
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"image_data": image_data.decode('utf-8')}),
            }
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Image not found"}),
            }
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Image ID is missing in the request"}),
        }



def delete_image(event, table_name, bucket_name):
    if "queryStringParameters" in event and "image_id" in event["queryStringParameters"]:
        image_id = event["queryStringParameters"]["image_id"]
        table = dynamodb_client.Table(table_name)

        # Prepare delete operations
        dynamodb_delete = {
            "operation": table.delete_item,
            "params": {"Key": {"id": image_id}}
        }
        s3_delete = {
            "operation": s3.delete_object,
            "params": {"Bucket": bucket_name, "Key": image_id + ".txt"}
        }

        # Fetch the content of the object in S3 before attempting deletion
        original_content = None
        try:
            s3_object = s3.get_object(Bucket=bucket_name, Key=image_id + ".txt")
            original_content = s3_object["Body"].read()
        except Exception as e:
            pass  # Ignore errors during fetching original content

        # Execute delete operations within a try-except block
        try:
            # Attempt to delete the item from DynamoDB
            dynamodb_delete["operation"](**dynamodb_delete["params"])

            # Attempt to delete the corresponding object from S3
            s3_delete["operation"](**s3_delete["params"])

            # If both delete operations succeed, return success response
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Image deleted successfully"}),
            }
        except Exception as e:
            # If any delete operation fails, attempt to rollback the other operation
            try:
                # Rollback the DynamoDB delete operation if S3 delete fails
                if "NoSuchKey" in str(e):
                    table.put_item(Item={"id": image_id})  # Add the item back to DynamoDB
                # Rollback the S3 delete operation if DynamoDB delete fails
                else:
                    if original_content is not None:
                        s3.put_object(Bucket=bucket_name, Key=image_id + ".txt", Body=original_content)  # Restore original content to S3
            except Exception as rollback_error:
                # If rollback fails, log the error and return a generic error response
                logger.error(f"Rollback failed: {rollback_error}")

            # Return a generic error response indicating failure to delete image
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": f"Failed to delete image: {str(e)}"}),
            }
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Image ID is missing in the request"}),
        }
