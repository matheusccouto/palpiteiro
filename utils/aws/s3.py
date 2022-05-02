"""Utils functions for AWS."""

import os

import boto3


def read_uri(uri):
    """Get bucket and key from S3 URI"""
    path = uri[5:]  # Exclude s3://
    bucket = path.split("/")[0]
    key = os.path.relpath(path, bucket)
    return bucket, key


def save(data, uri):
    """Save dict to an S3 as JSON file."""
    bucket, key = read_uri(uri)
    s3 = boto3.client("s3")
    s3.put_object(
        Body=data,
        Bucket=bucket,
        Key=key,
    )


def load(uri):
    """Load dict from a JSON in s3."""
    bucket, key = read_uri(uri)
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode()


def exists(uri):
    """Check if an object exists in S3."""
    bucket, key = read_uri(uri)
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket)
    return bool(list(bucket.objects.filter(Prefix=key)))


def delete(uri):
    """Delete a file from S3."""
    bucket, key = read_uri(uri)
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket)
    bucket.objects.filter(Prefix=key).delete()
