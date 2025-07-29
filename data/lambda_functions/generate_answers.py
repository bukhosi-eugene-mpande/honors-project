#!/usr/bin/env python3
"""
Lambda Function: Generate Answer Variations
==========================================

This Lambda function generates multiple answer variations using AWS Bedrock LLM.
"""

import json
import boto3
import os
from datetime import datetime
import random

def lambda_handler(event, context):
    """Generate answer variations using LLM"""
    
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-runtime')
    
    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    pipeline_id = event.get('body', {}).get('pipeline_id')
    rubrics = event.get('body', {}).get('rubrics', {})
    
    try:
        sample_questions = {
            "classes_objects": [
                "What is a constructor and how is it used in object-oriented programming?",
                "Explain the difference between a class and an object.",
                "What are access specifiers and why are they important?"
            ],
            "pointers_memory": [
                "What is a pointer and how do you declare one?",
                "Explain the concept of dereferencing a pointer.",
                "How does memory management work in C++?"
            ],
            "functions_scope": [
                "How do you define a function in C++?",
                "What is the difference between local and global variables?",
                "Explain function overloading with examples."
            ]
        }
        
        generated_answers = {}
        
        for topic_key, rubric in rubrics.items():
            questions = sample_questions.get(topic_key, [])
            topic_answers = {}
            
            for question in questions:
                variations = generate_answer_variations_with_llm(question, rubric, bedrock, model_id)
                topic_answers[question] = variations
            
            generated_answers[topic_key] = topic_answers
        
        # Store generated answers in S3
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/generated_answers/answers.json',
            Body=json.dumps(generated_answers, indent=2)
        )
        
        # Update pipeline metadata
        metadata_key = f'pipelines/{pipeline_id}/metadata.json'
        metadata_response = s3.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata = json.loads(metadata_response['Body'].read())
        
        metadata['steps_completed'].append('generate_answer_variations')
        metadata['current_step'] = 'nlp_assessment'
        metadata['answers_generated'] = sum(len(topic_answers) for topic_answers in generated_answers.values())
        metadata['updated_at'] = datetime.now().isoformat()
        
        s3.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2)
        )
        
        return {
            'statusCode': 200,
            'body': {
                'pipeline_id': pipeline_id,
                'status': 'answers_generated',
                'message': f'Generated answer variations for {len(generated_answers)} topics using LLM',
                'next_step': 'nlp_assessment',
                'generated_answers': generated_answers,
                'metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to generate answer variations with LLM'
            }
        }

def generate_answer_variations_with_llm(question: str, rubric: dict, bedrock_client, model_id: str) -> list:
    """Generate multiple answer variations using LLM based on rubric criteria"""
    variations = []
    
    # Generate perfect answer
    perfect_answer = generate_perfect_answer_with_llm(question, rubric, bedrock_client, model_id)
    variations.append({
        'type': 'perfect',
        'answer': perfect_answer,
        'expected_score': rubric['max_score']
    })
    
    # Generate partial answers (missing specific criteria)
    for i, criterion in enumerate(rubric['criteria']):
        partial_answer = generate_partial_answer_with_llm(question, rubric, [i], bedrock_client, model_id)
        variations.append({
            'type': f'partial_missing_{criterion["criterion"].lower().replace(" ", "_")}',
            'answer': partial_answer,
            'expected_score': rubric['max_score'] - criterion['points']
        })
    
    # Generate weak answer
    weak_answer = generate_weak_answer_with_llm(question, rubric, bedrock_client, model_id)
    variations.append({
        'type': 'weak',
        'answer': weak_answer,
        'expected_score': rubric['max_score'] * 0.3
    })
    
    # Generate incorrect answer
    incorrect_answer = generate_incorrect_answer_with_llm(question, rubric, bedrock_client, model_id)
    variations.append({
        'type': 'incorrect',
        'answer': incorrect_answer,
        'expected_score': 0
    })
    
    return variations

def generate_perfect_answer_with_llm(question: str, rubric: dict, bedrock_client, model_id: str) -> str:
    """Generate a perfect answer using LLM that meets all rubric criteria"""
    
    criteria_text = "\n".join([
        f"- {criterion['criterion']}: {criterion['description']} (Keywords: {', '.join(criterion['keywords'])})"
        for criterion in rubric['criteria']
    ])
    
    prompt = f"""You are an expert programming instructor. Generate a comprehensive answer to the following question that demonstrates complete understanding of all the specified criteria.

Question: {question}

Topic: {rubric['topic']}

Your answer must address ALL of the following criteria:
{criteria_text}

Requirements:
1. Address each criterion thoroughly and accurately
2. Use appropriate technical terminology
3. Provide clear explanations with examples where relevant
4. Ensure the answer is comprehensive and demonstrates deep understanding
5. Write in a clear, educational tone suitable for a programming student

Generate a detailed answer that would receive full marks (5/5 points) for this question:"""

    try:
        response = call_bedrock_llm(prompt, bedrock_client, model_id)
        return response.strip()
    except Exception as e:
        # Fallback to template-based generation
        return generate_perfect_answer_fallback(question, rubric)

def generate_partial_answer_with_llm(question: str, rubric: dict, exclude_criteria_indices: list, bedrock_client, model_id: str) -> str:
    """Generate a partial answer using LLM that meets some but not all criteria"""
    
    included_criteria = []
    excluded_criteria = []
    
    for i, criterion in enumerate(rubric['criteria']):
        if i not in exclude_criteria_indices:
            included_criteria.append(f"- {criterion['criterion']}: {criterion['description']}")
        else:
            excluded_criteria.append(f"- {criterion['criterion']}: {criterion['description']}")
    
    included_text = "\n".join(included_criteria)
    excluded_text = "\n".join(excluded_criteria)
    
    prompt = f"""You are an expert programming instructor. Generate a partial answer to the following question that demonstrates understanding of some but not all criteria.

Question: {question}

Topic: {rubric['topic']}

Your answer should address these criteria (include these):
{included_text}

Your answer should NOT address these criteria (omit these):
{excluded_text}

Requirements:
1. Address the included criteria adequately but not comprehensively
2. Completely avoid mentioning or explaining the excluded criteria
3. Use basic technical terminology
4. Provide simple explanations without deep detail
5. Write in a straightforward tone that shows partial understanding

Generate a partial answer that would receive partial marks for this question:"""

    try:
        response = call_bedrock_llm(prompt, bedrock_client, model_id)
        return response.strip()
    except Exception as e:
        # Fallback to template-based generation
        return generate_partial_answer_fallback(question, rubric, exclude_criteria_indices)

def generate_weak_answer_with_llm(question: str, rubric: dict, bedrock_client, model_id: str) -> str:
    """Generate a weak answer using LLM with minimal understanding"""
    
    prompt = f"""You are an expert programming instructor. Generate a weak answer to the following question that demonstrates minimal understanding.

Question: {question}

Topic: {rubric['topic']}

Requirements:
1. Show very basic understanding of the topic
2. Use simple, non-technical language
3. Provide vague or incomplete explanations
4. Avoid detailed technical concepts
5. Write as if the student has only a surface-level grasp of the material
6. Keep the answer short and lacking depth

Generate a weak answer that would receive low marks (around 30% of total points) for this question:"""

    try:
        response = call_bedrock_llm(prompt, bedrock_client, model_id)
        return response.strip()
    except Exception as e:
        # Fallback to template-based generation
        return generate_weak_answer_fallback(question, rubric)

def generate_incorrect_answer_with_llm(question: str, rubric: dict, bedrock_client, model_id: str) -> str:
    """Generate an incorrect answer using LLM with wrong concepts"""
    
    prompt = f"""You are an expert programming instructor. Generate an incorrect answer to the following question that demonstrates misunderstanding of the concepts.

Question: {question}

Topic: {rubric['topic']}

Requirements:
1. Include fundamental misconceptions about the topic
2. Mix up related but different concepts
3. Use incorrect technical terminology
4. Provide explanations that sound plausible but are wrong
5. Write as if the student has learned the concepts incorrectly
6. Make the answer seem confident but factually incorrect

Generate an incorrect answer that would receive zero marks for this question:"""

    try:
        response = call_bedrock_llm(prompt, bedrock_client, model_id)
        return response.strip()
    except Exception as e:
        # Fallback to template-based generation
        return generate_incorrect_answer_fallback(question, rubric)

def call_bedrock_llm(prompt: str, bedrock_client, model_id: str) -> str:
    """Call AWS Bedrock LLM with the given prompt"""
    
    if 'claude' in model_id.lower():
        # Claude model format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    else:
        # Default format for other models
        body = {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7
        }
    
    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'claude' in model_id.lower():
            return response_body['content'][0]['text']
        else:
            return response_body.get('completion', response_body.get('generated_text', ''))
            
    except Exception as e:
        raise Exception(f"LLM call failed: {str(e)}")


def generate_partial_answer_fallback(question: str, rubric: dict, exclude_criteria_indices: list) -> str:
    """Fallback partial answer generation"""
    answer_parts = []
    
    for i, criterion in enumerate(rubric['criteria']):
        if i not in exclude_criteria_indices:
            if "Classes & Objects" in rubric['topic']:
                if "constructor" in criterion['criterion'].lower():
                    answer_parts.append("A constructor is called when an object is created.")
                elif "class definition" in criterion['criterion'].lower():
                    answer_parts.append("A class has data members and functions.")
                elif "access specifiers" in criterion['criterion'].lower():
                    answer_parts.append("There are public and private members in a class.")
            
            elif "Pointers & Memory" in rubric['topic']:
                if "pointer declaration" in criterion['criterion'].lower():
                    answer_parts.append("A pointer stores an address.")
                elif "dereferencing" in criterion['criterion'].lower():
                    answer_parts.append("You use * to get the value from a pointer.")
                elif "memory management" in criterion['criterion'].lower():
                    answer_parts.append("Memory can be allocated and freed.")
            
            elif "Functions & Scope" in rubric['topic']:
                if "function definition" in criterion['criterion'].lower():
                    answer_parts.append("A function has a name and parameters.")
                elif "variable scope" in criterion['criterion'].lower():
                    answer_parts.append("Variables have different scopes.")
                elif "function overloading" in criterion['criterion'].lower():
                    answer_parts.append("Functions can have the same name.")
    
    return " ".join(answer_parts) if answer_parts else "I don't know much about this topic."

def generate_weak_answer_fallback(question: str, rubric: dict) -> str:
    """Fallback weak answer generation"""
    if "Classes & Objects" in rubric['topic']:
        return "A class is like a template for objects. It can have functions and data."
    elif "Pointers & Memory" in rubric['topic']:
        return "A pointer points to something in memory. You can use it to access data."
    elif "Functions & Scope" in rubric['topic']:
        return "Functions are blocks of code that do something. Variables can be local or global."
    else:
        return "This is related to programming concepts."

def generate_incorrect_answer_fallback(question: str, rubric: dict) -> str:
    """Fallback incorrect answer generation"""
    if "Classes & Objects" in rubric['topic']:
        return "A class is the same as a function. You can only have one constructor and it must be public."
    elif "Pointers & Memory" in rubric['topic']:
        return "A pointer is just another variable type like int. You don't need to worry about memory management."
    elif "Functions & Scope" in rubric['topic']:
        return "Functions are only for mathematical calculations. All variables should be global for easy access."
    else:
        return "This concept is not important in programming." 