def GenerateConfig(context):
    resources = []

    chains = ['arbitrum_nova']
    entity_types = ['blocks', 'transactions', 'logs', 'token_transfers', 'traces', 'contracts', 'tokens']

    for chain in chains:
        topic_name_prefix = chain
        subscription_name_prefix = chain + '.bigquery'
        # 7 days
        message_retention_duration = '604800s'

        for entity_type in entity_types:
            topic_name = topic_name_prefix + '.' + entity_type
            topic_resource_name = topic_name.replace('.', '-')
            subscription_name = subscription_name_prefix + '.' + entity_type
            subscription_resource_name = subscription_name.replace('.', '-')
            resources.append({
                'name': topic_resource_name,
                'type': 'pubsub.v1.topic',
                'properties': {
                    'topic': topic_name
                },
                'schemaSettings' : {
                    'encoding' : 'JSON',
                    'schema' : 'projects/circle-ds-pipelines/schemas/evmLog_proto2'
                }
            })
            
            resources.append({
                'name': subscription_resource_name,
                'type': 'pubsub.v1.subscription',
                'properties': {
                    'subscription': subscription_name,
                    'topic': '$(ref.' + topic_resource_name + '.name)',
                    'ackDeadlineSeconds': 120,
                    'retainAckedMessages': True,
                    'messageRetentionDuration': message_retention_duration,
                    'expirationPolicy': {
                    }
                }
            })

    return {'resources': resources}


if __name__ == '__main__':
    res = GenerateConfig(None)
    print(res)
