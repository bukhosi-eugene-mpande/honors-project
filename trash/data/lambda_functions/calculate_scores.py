#!/usr/bin/env python3
"""
Lambda Function: Calculate Scores
================================

This Lambda function calculates and aggregates scores from NLP assessment.
"""

import json
import boto3
import os
from datetime import datetime
import numpy as np

def lambda_handler(event, context):
    """Calculate and aggregate scores from NLP assessment"""

    s3 = boto3.client('s3')

    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')

    pipeline_id = event.get('body', {}).get('pipeline_id')
    nlp_results = event.get('body', {}).get('nlp_results', {})
    
    try:
        score_analysis = {}
        overall_stats = {
            'total_answers': 0,
            'total_score': 0,
            'avg_score': 0,
            'score_distribution': {},
            'topic_performance': {},
            'answer_type_performance': {},
            'nlp_metrics': {
                'sentiment_distribution': {},
                'complexity_distribution': {},
                'key_phrases_analysis': {}
            }
        }
        
        for topic_key, topic_results in nlp_results.items():
            topic_stats = {
                'total_answers': 0,
                'total_score': 0,
                'avg_score': 0,
                'answer_types': {},
                'score_distribution': {},
                'nlp_metrics': {
                    'sentiments': [],
                    'complexities': [],
                    'key_phrases': []
                }
            }
            
            for question, variations in topic_results.items():
                question_stats = {
                    'total_variations': len(variations),
                    'scores': [],
                    'answer_types': {},
                    'nlp_metrics': {
                        'sentiments': [],
                        'complexities': [],
                        'key_phrases': []
                    }
                }
                
                for variation in variations:
                    final_score = variation['final_score']
                    answer_type = variation['type']
                    nlp_analysis = variation['nlp_analysis']
                    
                    overall_stats['total_answers'] += 1
                    overall_stats['total_score'] += final_score
                    
                    topic_stats['total_answers'] += 1
                    topic_stats['total_score'] += final_score
                    topic_stats['answer_types'][answer_type] = topic_stats['answer_types'].get(answer_type, 0) + 1
                    
                    question_stats['scores'].append(final_score)
                    question_stats['answer_types'][answer_type] = question_stats['answer_types'].get(answer_type, 0) + 1
                    
                    sentiment = nlp_analysis['sentiment']['sentiment']
                    complexity = nlp_analysis['complexity']['complexity_level']
                    key_phrases = nlp_analysis['key_phrases']
                    
                    overall_stats['nlp_metrics']['sentiment_distribution'][sentiment] = overall_stats['nlp_metrics']['sentiment_distribution'].get(sentiment, 0) + 1
                    overall_stats['nlp_metrics']['complexity_distribution'][complexity] = overall_stats['nlp_metrics']['complexity_distribution'].get(complexity, 0) + 1
                    overall_stats['answer_type_performance'][answer_type] = overall_stats['answer_type_performance'].get(answer_type, 0) + final_score

                    topic_stats['nlp_metrics']['sentiments'].append(sentiment)
                    topic_stats['nlp_metrics']['complexities'].append(complexity)
                    topic_stats['nlp_metrics']['key_phrases'].extend(key_phrases)
                    
                    question_stats['nlp_metrics']['sentiments'].append(sentiment)
                    question_stats['nlp_metrics']['complexities'].append(complexity)
                    question_stats['nlp_metrics']['key_phrases'].extend(key_phrases)

                if question_stats['scores']:
                    question_stats['avg_score'] = np.mean(question_stats['scores'])
                    question_stats['std_score'] = np.std(question_stats['scores'])
                    question_stats['min_score'] = min(question_stats['scores'])
                    question_stats['max_score'] = max(question_stats['scores'])
                
                topic_stats['questions'] = topic_stats.get('questions', {})
                topic_stats['questions'][question] = question_stats
            
            if topic_stats['total_answers'] > 0:
                topic_stats['avg_score'] = topic_stats['total_score'] / topic_stats['total_answers']
                
                all_scores = []
                for question_data in topic_stats['questions'].values():
                    all_scores.extend(question_data['scores'])
                
                topic_stats['score_distribution'] = calculate_score_distribution(all_scores)

                topic_stats['nlp_metrics']['sentiment_distribution'] = calculate_distribution(topic_stats['nlp_metrics']['sentiments'])
                topic_stats['nlp_metrics']['complexity_distribution'] = calculate_distribution(topic_stats['nlp_metrics']['complexities'])
                topic_stats['nlp_metrics']['key_phrases_frequency'] = calculate_key_phrases_frequency(topic_stats['nlp_metrics']['key_phrases'])
            
            score_analysis[topic_key] = topic_stats
            overall_stats['topic_performance'][topic_key] = topic_stats['avg_score']
        
        if overall_stats['total_answers'] > 0:
            overall_stats['avg_score'] = overall_stats['total_score'] / overall_stats['total_answers']
            
            all_scores = []
            for topic_data in score_analysis.values():
                for question_data in topic_data['questions'].values():
                    all_scores.extend(question_data['scores'])
            
            overall_stats['score_distribution'] = calculate_score_distribution(all_scores)
            
            for answer_type, total_score in overall_stats['answer_type_performance'].items():
                count = sum(1 for topic_data in score_analysis.values() 
                           for question_data in topic_data['questions'].values()
                           for variation in question_data.get('variations', [])
                           if variation.get('type') == answer_type)
                if count > 0:
                    overall_stats['answer_type_performance'][answer_type] = total_score / count
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/scores/score_analysis.json',
            Body=json.dumps({
                'score_analysis': score_analysis,
                'overall_stats': overall_stats
            })
        )
        
        metadata_key = f'pipelines/{pipeline_id}/metadata.json'
        metadata_response = s3.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata = json.loads(metadata_response['Body'].read())
        
        metadata['steps_completed'].append('nlp_assessment')
        metadata['current_step'] = 'score_calculation'
        metadata['score_analysis_completed'] = True
        metadata['total_answers_processed'] = overall_stats['total_answers']
        metadata['overall_avg_score'] = overall_stats['avg_score']
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
                'status': 'score_calculation_complete',
                'message': f'Score calculation completed for {overall_stats["total_answers"]} answers',
                'next_step': 'results_analysis',
                'score_analysis': score_analysis,
                'overall_stats': overall_stats,
                'metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to calculate scores'
            }
        }

def calculate_score_distribution(scores: list) -> dict:
    """Calculate distribution of scores"""
    if not scores:
        return {}
    
    # Define score ranges
    ranges = [
        (0, 1, 'Very Low (0-1)'),
        (1, 2, 'Low (1-2)'),
        (2, 3, 'Below Average (2-3)'),
        (3, 4, 'Average (3-4)'),
        (4, 5, 'Above Average (4-5)')
    ]
    
    distribution = {}
    for min_score, max_score, label in ranges:
        count = sum(1 for score in scores if min_score <= score < max_score)
        distribution[label] = count
    
    return distribution

def calculate_distribution(items: list) -> dict:
    """Calculate distribution of items"""
    distribution = {}
    for item in items:
        distribution[item] = distribution.get(item, 0) + 1
    return distribution

def calculate_key_phrases_frequency(key_phrases: list) -> dict:
    """Calculate frequency of key phrases"""
    frequency = {}
    for phrase in key_phrases:
        frequency[phrase] = frequency.get(phrase, 0) + 1
    
    # Sort by frequency and return top 20
    sorted_frequency = dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
    return dict(list(sorted_frequency.items())[:20]) 