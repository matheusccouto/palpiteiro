"""Create README.md state machines diagrams."""

# pylint: disable=expression-not-assigned

import os

from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.custom import Custom
from diagrams.gcp.analytics import Bigquery

THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")
