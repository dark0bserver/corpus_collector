import boto3
import botocore
import json
import os
import random
from build_corpus import get_warc_indices_for_domain
from build_corpus import get_text_for_index


def queue_domain(event, context):
    """Extract domain of interest and queue WET fetches
    """

    domain = event['domain']
    fetch_limit = int(os.environ['PAGE_FETCH_LIMIT'])
    if 'limit' in event:
        fetch_limit = int(event['limit'])

    index = os.environ['CC_INDEX']
    if 'index' in event:
        index = event['index']

    # pull all entries for this domain from index
    indices = list(get_warc_indices_for_domain(domain, index))

    # sample returned indices to 'limit' (where they exceed 'limit')
    sampled_indices = indices
    if fetch_limit < len(indices):
        sampled_indices = random.sample(indices, fetch_limit)

    # for each sampled index, get stored page text by URL
    lambda_client = boto3.client('lambda')

    results = list()

    for index in sampled_indices:
        results.append(
            lambda_client.invoke(
                FunctionName='fetch_wet_entry',
                Payload=json.dumps(index),
                InvocationType='Event'
            )
        )

    return {
        "total_index_count": len(indices),
        "requested_indices": sampled_indices
    }


def fetch_wet_entry(event, context):
    # retreive WET entry for index, error string otherwise
    results = dict()
    results['url'] = event['url']

    try:
        results['content'] = get_text_for_index(event)['content']
    except botocore.exceptions.ClientError as e:
        results['error'] = f'Error retrieving: {event} | {e}'

    # store result into DynamoDB
    db = boto3.resource('dynamodb')
    table = db.Table('page_text')
    response = table.put_item(Item=results)

    return response
