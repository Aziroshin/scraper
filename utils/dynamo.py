"""Functionality related to DynamoDB."""

import boto3

TABLE_NAME = "TechForUkraine-CIG"

client = boto3.client("dynamodb", region_name="us-east-1")

def write_to_dynamo(country: str, general: list, reception: list, source: str):
    """
    Write the data to DynamoDB.

    Args:
        country (str): The name of the country.
        general (list[str]): More general information.
        reception (list): Border crossing points.
    """

    general_list = []
    for line in general:
        general_list.append({ "S": line })

    reception_list = []
    for rec in reception:
        reception_list.append({
            "M": {
                "name": { "S": rec.name },
                "lat": { "S": rec.lat },
                "lon": { "S": rec.lon },
                "address": { "S": rec.address },
                "qr": { "S": rec.qr }
            }
        })

    client.put_item(
        TableName = TABLE_NAME,
        Item = {
            "country": { "S": country },
            "general": { "L": general_list },
            "reception": { "L": reception_list },
            "source": { "S": source }
        })
