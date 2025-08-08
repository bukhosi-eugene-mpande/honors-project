#!/usr/bin/env python3
"""
Lambda Function: NLP Assessment
==============================

This Lambda function performs NLP-based assessment of answers using AWS Comprehend.
"""

import json
import boto3
import os
from datetime import datetime
import re

def lambda_handler(event, context):
    """Perform NLP-based assessment of answers"""
    
    s3 = boto3.client('s3')
    comprehend = boto3.client('comprehend')
    
    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')
    
    pipeline_id = event.get('body', {}).get('pipeline_id')
    generated_answers = event.get('body', {}).get('generated_answers', {})
    
    try:
        nlp_results = {}
        
        for topic_key, topic_answers in generated_answers.items():
            topic_results = {}
            
            for question, variations in topic_answers.items():
                question_results = []
                
                for variation in variations:
                    answer = variation['answer']
                    answer_type = variation['type']
                    expected_score = variation['expected_score']
                    
                    nlp_analysis = perform_nlp_analysis(answer, comprehend)
                    
                    rubric_score = calculate_rubric_score(answer, topic_key)
                    
                    final_score = combine_scores(nlp_analysis, rubric_score, expected_score)
                    
                    question_results.append({
                        'type': answer_type,
                        'answer': answer,
                        'expected_score': expected_score,
                        'nlp_analysis': nlp_analysis,
                        'rubric_score': rubric_score,
                        'final_score': final_score,
                        'feedback': generate_feedback(final_score, expected_score)
                    })
                
                topic_results[question] = question_results
            
            nlp_results[topic_key] = topic_results
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/nlp_results/assessment_results.json',
            Body=json.dumps(nlp_results)
        )
        
        metadata_key = f'pipelines/{pipeline_id}/metadata.json'
        metadata_response = s3.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata = json.loads(metadata_response['Body'].read())
        
        metadata['steps_completed'].append('generate_answer_variations')
        metadata['current_step'] = 'nlp_assessment'
        metadata['nlp_results_generated'] = len(nlp_results)
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
                'status': 'nlp_assessment_complete',
                'message': f'NLP assessment completed for {len(nlp_results)} topics',
                'next_step': 'score_calculation',
                'nlp_results': nlp_results,
                'metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to perform NLP assessment'
            }
        }

def perform_nlp_analysis(answer: str, comprehend_client) -> dict:
    """Perform comprehensive NLP analysis on the answer"""
    
    try:
        sentiment_response = comprehend_client.detect_sentiment(
            Text=answer,
            LanguageCode='en'
        )
        
        key_phrases_response = comprehend_client.detect_key_phrases(
            Text=answer,
            LanguageCode='en'
        )
        
        entities_response = comprehend_client.detect_entities(
            Text=answer,
            LanguageCode='en'
        )
        
        syntax_response = comprehend_client.detect_syntax(
            Text=answer,
            LanguageCode='en'
        )
        
        complexity_analysis = analyze_text_complexity(answer)
        
        return {
            'sentiment': {
                'sentiment': sentiment_response['Sentiment'],
                'confidence': sentiment_response['SentimentScore']
            },
            'key_phrases': [phrase['Text'] for phrase in key_phrases_response['KeyPhrases']],
            'entities': [entity['Text'] for entity in entities_response['Entities']],
            'syntax': {
                'tokens': len(syntax_response['SyntaxTokens']),
                'parts_of_speech': analyze_parts_of_speech(syntax_response['SyntaxTokens'])
            },
            'complexity': complexity_analysis
        }
        
    except Exception as e:  
        return perform_fallback_analysis(answer)

def perform_fallback_analysis(answer: str) -> dict:
    """Perform basic NLP analysis without AWS Comprehend"""
    
    positive_words = ['correct', 'proper', 'good', 'right', 'accurate', 'clear', 'understand', 'know']
    negative_words = ['wrong', 'incorrect', 'bad', 'confused', 'unclear', "don't", 'not']
    
    words = answer.lower().split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        sentiment = 'POSITIVE'
        confidence = {'Positive': 0.7, 'Negative': 0.2, 'Neutral': 0.1}
    elif negative_count > positive_count:
        sentiment = 'NEGATIVE'
        confidence = {'Positive': 0.2, 'Negative': 0.7, 'Neutral': 0.1}
    else:
        sentiment = 'NEUTRAL'
        confidence = {'Positive': 0.3, 'Negative': 0.3, 'Neutral': 0.4}
    
    key_phrases = extract_simple_key_phrases(answer)
    
    complexity = analyze_text_complexity(answer)
    
    return {
        'sentiment': {
            'sentiment': sentiment,
            'confidence': confidence
        },
        'key_phrases': key_phrases,
        'entities': [],
        'syntax': {
            'tokens': len(words),
            'parts_of_speech': {}
        },
        'complexity': complexity
    }

def extract_simple_key_phrases(answer: str) -> list:
    """Extract key phrases using simple NLP techniques"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    words = answer.lower().split()
    key_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    phrases = []
    current_phrase = []
    
    for word in key_words:
        if current_phrase and word in current_phrase[-1] or current_phrase and current_phrase[-1] in word:
            current_phrase.append(word)
        else:
            if current_phrase:
                phrases.append(' '.join(current_phrase))
            current_phrase = [word]
    
    if current_phrase:
        phrases.append(' '.join(current_phrase))
    
    return phrases[:10]

def analyze_text_complexity(answer: str) -> dict:
    """Analyze text complexity metrics"""
    words = answer.split()
    sentences = re.split(r'[.!?]+', answer)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    word_count = len(words)
    sentence_count = len(sentences)
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    unique_words = len(set(words))
    lexical_diversity = unique_words / word_count if word_count > 0 else 0
    
    syllable_count = sum(count_syllables(word) for word in words)
    avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
    
    flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    flesch_score = max(0, min(100, flesch_score))
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_sentence_length': avg_sentence_length,
        'lexical_diversity': lexical_diversity,
        'avg_syllables_per_word': avg_syllables_per_word,
        'flesch_reading_ease': flesch_score,
        'complexity_level': get_complexity_level(flesch_score)
    }

def count_syllables(word: str) -> int:
    """Approximate syllable count for a word"""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    on_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not on_vowel:
            count += 1
        on_vowel = is_vowel
    
    if word.endswith('e'):
        count -= 1
    if count == 0:
        count = 1
    
    return count

def get_complexity_level(flesch_score: float) -> str:
    """Get complexity level based on Flesch Reading Ease score"""
    if flesch_score >= 90:
        return 'very_easy'
    elif flesch_score >= 80:
        return 'easy'
    elif flesch_score >= 70:
        return 'fairly_easy'
    elif flesch_score >= 60:
        return 'standard'
    elif flesch_score >= 50:
        return 'fairly_difficult'
    elif flesch_score >= 30:
        return 'difficult'
    else:
        return 'very_difficult'

def analyze_parts_of_speech(syntax_tokens: list) -> dict:
    """Analyze parts of speech distribution"""
    pos_counts = {}
    
    for token in syntax_tokens:
        pos = token['PartOfSpeech']['Tag']
        pos_counts[pos] = pos_counts.get(pos, 0) + 1
    
    return pos_counts

def calculate_rubric_score(answer: str, topic_key: str) -> dict:
    """Calculate score based on rubric criteria"""
    
    rubric_keywords = {
        'classes_objects': {
            'class_definition': ['class', 'data members', 'member functions', 'attributes', 'methods'],
            'constructor': ['constructor', 'initialization', 'object creation', 'default constructor'],
            'access_specifiers': ['public', 'private', 'protected', 'access', 'visibility']
        },
        'pointers_memory': {
            'pointer_declaration': ['pointer', 'address', '&', '*', 'memory address'],
            'dereferencing': ['dereference', '*', 'value', 'content', 'indirection'],
            'memory_management': ['malloc', 'free', 'new', 'delete', 'memory allocation']
        },
        'functions_scope': {
            'function_definition': ['function', 'return type', 'parameters', 'arguments', 'definition'],
            'variable_scope': ['scope', 'local', 'global', 'variable', 'visibility'],
            'function_overloading': ['overloading', 'same name', 'different parameters', 'signature']
        }
    }
    
    topic_keywords = rubric_keywords.get(topic_key, {})
    answer_lower = answer.lower()
    
    criterion_scores = {}
    total_score = 0
    
    for criterion, keywords in topic_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in answer_lower)
        score = min(2, matches)
        criterion_scores[criterion] = score
        total_score += score
    
    return {
        'criterion_scores': criterion_scores,
        'total_score': total_score,
        'max_possible_score': len(topic_keywords) * 2
    }

def combine_scores(nlp_analysis: dict, rubric_score: dict, expected_score: float) -> float:
    """Combine NLP analysis and rubric scores"""
    
    sentiment_score = nlp_analysis['sentiment']['confidence'].get('POSITIVE', 0.5)
    complexity_score = nlp_analysis['complexity']['lexical_diversity']
    key_phrases_count = len(nlp_analysis['key_phrases'])
    
    rubric_normalized = rubric_score['total_score'] / rubric_score['max_possible_score']
    
    final_score = (
        rubric_normalized * 0.6 +
        sentiment_score * 0.2 +
        complexity_score * 0.1 +
        min(1.0, key_phrases_count / 5) * 0.1
    )
    
    return final_score * expected_score

def generate_feedback(final_score: float, expected_score: float) -> str:
    """Generate feedback based on score performance"""
    percentage = final_score / expected_score if expected_score > 0 else 0
    
    if percentage >= 0.9:
        return "Excellent answer that demonstrates comprehensive understanding."
    elif percentage >= 0.7:
        return "Good answer with solid understanding of the concepts."
    elif percentage >= 0.5:
        return "Adequate answer showing some understanding but needs improvement."
    elif percentage >= 0.3:
        return "Limited understanding demonstrated. Review the concepts."
    else:
        return "Significant gaps in understanding. Additional study required." 