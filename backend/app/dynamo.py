import os
import boto3

DDB_REGION = os.getenv("AWS_REGION", "us-east-1")
CATALOG_TABLE = os.getenv("CATALOG_TABLE", "SurveyCatalog")
RESPONSES_TABLE = os.getenv("RESPONSES_TABLE", "SurveyResponses")

dynamodb = boto3.resource("dynamodb", region_name=DDB_REGION)

def catalog_table():
    return dynamodb.Table(CATALOG_TABLE)

def responses_table():
    return dynamodb.Table(RESPONSES_TABLE)
