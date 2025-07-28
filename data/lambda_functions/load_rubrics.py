#!/usr/bin/env python3
"""
Lambda Function: Load Rubrics
============================

This Lambda function loads rubrics from S3 or DynamoDB.
"""

import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """Load rubrics for assessment"""

    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')

    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')
    table_name = os.environ.get('RUBRIC_TABLE', 'rubrics')

    pipeline_id = event.get('body', {}).get('pipeline_id')
    
    try:
        rubrics = {}
        
        sample_rubrics = {
            "classes_objects": {
                "topic": "Classes & Objects",
                "criteria": [
                    {
                        "criterion": "Class Definition Understanding",
                        "description": "Student demonstrates understanding of class structure",
                        "points": 2,
                        "keywords": ["class", "data members", "member functions", "attributes", "methods"]
                    },
                    {
                        "criterion": "Constructor Knowledge",
                        "description": "Student understands constructor purpose and usage",
                        "points": 2,
                        "keywords": ["constructor", "initialization", "object creation", "default constructor"]
                    },
                    {
                        "criterion": "Access Specifiers",
                        "description": "Student knows about public, private, protected",
                        "points": 1,
                        "keywords": ["public", "private", "protected", "access", "visibility"]
                    }
                ],
                "max_score": 5
            },
            "pointers_memory": {
                "topic": "Pointers & Memory",
                "criteria": [
                    {
                        "criterion": "Pointer Declaration",
                        "description": "Student can declare and initialize pointers",
                        "points": 2,
                        "keywords": ["pointer", "address", "&", "*", "memory address"]
                    },
                    {
                        "criterion": "Dereferencing",
                        "description": "Student understands pointer dereferencing",
                        "points": 2,
                        "keywords": ["dereference", "*", "value", "content", "indirection"]
                    },
                    {
                        "criterion": "Memory Management",
                        "description": "Student understands memory allocation concepts",
                        "points": 1,
                        "keywords": ["malloc", "free", "new", "delete", "memory allocation"]
                    }
                ],
                "max_score": 5
            },
            "functions_scope": {
                "topic": "Functions & Scope",
                "criteria": [
                    {
                        "criterion": "Function Definition",
                        "description": "Student can define functions with proper syntax",
                        "points": 2,
                        "keywords": ["function", "return type", "parameters", "arguments", "definition"]
                    },
                    {
                        "criterion": "Variable Scope",
                        "description": "Student understands local vs global scope",
                        "points": 2,
                        "keywords": ["scope", "local", "global", "variable", "visibility"]
                    },
                    {
                        "criterion": "Function Overloading",
                        "description": "Student understands function overloading",
                        "points": 1,
                        "keywords": ["overloading", "same name", "different parameters", "signature"]
                    }
                ],
                "max_score": 5
            }
        }
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/rubrics/rubrics.json',
            Body=json.dumps(sample_rubrics)
        )
        
        metadata_key = f'pipelines/{pipeline_id}/metadata.json'
        metadata_response = s3.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata = json.loads(metadata_response['Body'].read())
        
        metadata['steps_completed'].append('initialize_pipeline')
        metadata['current_step'] = 'load_rubrics'
        metadata['rubrics_loaded'] = list(sample_rubrics.keys())
        metadata['updated_at'] = datetime.now().isoformat()
        
        s3.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=json.dumps(metadata)
        )
        
        return {
            'statusCode': 200,
            'body': {
                'pipeline_id': pipeline_id,
                'status': 'rubrics_loaded',
                'message': f'Loaded {len(sample_rubrics)} rubrics successfully',
                'next_step': 'generate_answer_variations',
                'rubrics': sample_rubrics,
                'metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to load rubrics'
            }
        } 