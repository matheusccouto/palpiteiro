"""Utils functions for AWS."""

import json
import os

import boto3
import urllib3


def get(url):
    """Make a GET request without specifying any body or header."""
    return json.loads(urllib3.PoolManager().request("GET", url).data.decode("utf-8"))


def to_s3(data, bucket, key):
    """Save dict to an S3 as JSON file."""
    s3 = boto3.client("s3")
    s3.put_object(
        Body=json.dumps(data),
        Bucket=bucket,
        Key=key,
    )
    return f"s3://{bucket}/{key}"


def read_uri(uri):
    """Get bucket and key from S3 URI"""
    path = uri[5:]  # Exclude s3://
    bucket = path.split("/")
    key = os.path.relpath(path, bucket)
    return bucket, key


def exists(uri):
    """Check if an object exists in S2."""
    bucket, key = read_uri(uri)
    s3 = boto3.client("s3")
    bucket = s3.Bucket(bucket)
    return bool(list(bucket.objects.filter(Prefix=key)))