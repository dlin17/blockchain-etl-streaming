from google.cloud import pubsub_v1, bigquery
from google.auth import default
from google.cloud.bigquery import TimePartitioningType, TimePartitioning

import sys

# Get the default credentials
creds, project_id = default()

dataset_id = sys.argv[1]
entity_types = [
    "blocks",
    "transactions",
    "logs",
    "token_transfers",
    # "traces",
    # "contracts",
    # "tokens",
]
client = bigquery.Client()
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

# create dataset if not exists
dataset_ref = client.dataset(dataset_id)
try:
    client.get_dataset(dataset_ref)
    print(f"Dataset {dataset_ref.dataset_id} already exists")
except:
    client.create_dataset(dataset_ref)
    print(f"Created dataset {dataset_ref.dataset_id}")

for entity_type in entity_types:
    # create table in bigquery if not exists
    table_schema_path = f"table_schemas/{entity_type}.json"
    table_id = f"{project_id}.{dataset_id}.{entity_type}"
    table_schema = client.schema_from_json(table_schema_path)

    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists")
    except:
        table = bigquery.Table(table_id, schema=table_schema)
        partition_key = "timestamp" if entity_type == "blocks" else "block_timestamp"
        table.time_partitioning = TimePartitioning(
            type_=TimePartitioningType.DAY, field=partition_key
        )
        table.clustering_fields = [partition_key]

        table = client.create_table(table)
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

    topic_id = f"{dataset_id}.{entity_type}"

    topic_path = publisher.topic_path(project_id, topic_id)
    schema_path = f"projects/{project_id}/schemas/{entity_type}"

    # create topic if not exists, update schema if exists
    request = {
        "name": topic_path,
        "schema_settings": {"schema": schema_path, "encoding": "JSON"},
    }
    try:
        publisher.get_topic(request={"topic": topic_path})
        print(f"Topic {topic_path} already exists")

    except:
        topic = publisher.create_topic(request=request)
        print(f"Created topic: {topic.name}")

    # create pubsub to bigquery subscription if not exists
    subscription_id = f"{dataset_id}.{entity_type}.bigquery"
    subscription_path = publisher.subscription_path(project_id, subscription_id)

    bigquery_config = pubsub_v1.types.BigQueryConfig(
        table=table_id,
        use_topic_schema=True,
        write_metadata=False,
        drop_unknown_fields=True,
    )

    # Wrap the subscriber in a 'with' block to automatically call close() to
    # close the underlying gRPC channel when done.
    # create if not exists
    try:
        subscriber.get_subscription(request={"subscription": subscription_path})
        print(f"Subscription {subscription_path} already exists")
    except:
        subscription = subscriber.create_subscription(
            request={
                "name": subscription_path,
                "topic": f"projects/{project_id}/topics/{dataset_id}.{entity_type}",
                "bigquery_config": bigquery_config,
                "ack_deadline_seconds": 120,
            }
        )
        print(f"BigQuery subscription created: {subscription_path}.")
        print(f"Table for subscription is: {table_id}")
