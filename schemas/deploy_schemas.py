import os

from google.api_core.exceptions import AlreadyExists
from google.cloud.pubsub import SchemaServiceClient
from google.pubsub_v1.types import Schema
from google.auth import default

# Get the default credentials
creds, project_id = default()
project_path = f"projects/{project_id}"

protobuf_folder = "protobuf"

for filename in os.listdir(protobuf_folder):
    if filename.endswith(".proto"):
        proto_file = os.path.join(protobuf_folder, filename)
        schema_id = filename.replace(".proto", "")

    with open(proto_file, "rb") as f:
        src = f.read().decode("utf-8")

    schema_client = SchemaServiceClient()
    schema_path = schema_client.schema_path(project_id, schema_id)
    schema = Schema(name=schema_path, type_=Schema.Type.PROTOCOL_BUFFER, definition=src)

    try:
        result = schema_client.create_schema(
            request={"parent": project_path, "schema": schema, "schema_id": schema_id}
        )
        print(f"Created a schema using schema file:\n{result}")
    except AlreadyExists:
        print(f"{schema_id} already exists.")