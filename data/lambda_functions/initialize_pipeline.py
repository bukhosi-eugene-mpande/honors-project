#!/usr/bin/env python3
"""
Lambda Function: Initialize Pipeline
===================================

This Lambda function initializes the rubric assessment pipeline.
"""

import json
import boto3
import os
from datetime import datetime
import uuid

def lambda_handler(event, context):
    """Initialize the assessment pipeline"""
    
    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')
    
    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')
    table_name = os.environ.get('ASSESSMENT_TABLE', 'rubric-assessments')
    
    pipeline_id = str(uuid.uuid4())
    
    pipeline_metadata = {
        'pipeline_id': pipeline_id,
        'status': 'initialized',
        'created_at': datetime.now().isoformat(),
        'input_data': event,
        'steps_completed': [],
        'current_step': 'initialize_pipeline'
    }
    
    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                'pipeline_id': {'S': pipeline_id},
                'metadata': {'S': json.dumps(pipeline_metadata)},
                'created_at': {'S': pipeline_metadata['created_at']}
            }
        )
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/metadata.json',
            Body=json.dumps(pipeline_metadata)
        )
        
        folders = [
            'rubrics/',
            'generated_answers/',
            'nlp_results/',
            'scores/',
            'reports/'
        ]
        
        for folder in folders:
            s3.put_object(
                Bucket=bucket_name,
                Key=f'pipelines/{pipeline_id}/{folder}'
            )
        
        return {
            'statusCode': 200,
            'body': {
                'pipeline_id': pipeline_id,
                'status': 'initialized',
                'message': 'Pipeline initialized successfully',
                'next_step': 'load_rubrics',
                'metadata': pipeline_metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to initialize pipeline'
            }
        } 