#!/usr/bin/env python3
"""
Lambda Function: Generate Answer Variations
==========================================

This Lambda function generates multiple answer variations based on rubrics.
"""

import json
import boto3
import os
from datetime import datetime
import random

def lambda_handler(event, context):
    """Generate answer variations based on rubrics"""
    
    s3 = boto3.client('s3')
    
    bucket_name = os.environ.get('ASSESSMENT_BUCKET', 'rubric-assessment-bucket')
    
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
                variations = generate_answer_variations(question, rubric)
                topic_answers[question] = variations
            
            generated_answers[topic_key] = topic_answers
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'pipelines/{pipeline_id}/generated_answers/answers.json',
            Body=json.dumps(generated_answers)
        )
        
        metadata_key = f'pipelines/{pipeline_id}/metadata.json'
        metadata_response = s3.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata = json.loads(metadata_response['Body'].read())
        
        metadata['steps_completed'].append('load_rubrics')
        metadata['current_step'] = 'generate_answer_variations'
        metadata['answers_generated'] = len(generated_answers)
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
                'status': 'answers_generated',
                'message': f'Generated answer variations for {len(generated_answers)} topics',
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
                'message': 'Failed to generate answer variations'
            }
        }

def generate_answer_variations(question: str, rubric: dict) -> list:
    """Generate multiple answer variations based on rubric criteria"""
    variations = []
    
    perfect_answer = generate_perfect_answer(question, rubric)
    variations.append({
        'type': 'perfect',
        'answer': perfect_answer,
        'expected_score': rubric['max_score']
    })
    
    for i, criterion in enumerate(rubric['criteria']):
        partial_answer = generate_partial_answer(question, rubric, exclude_criteria=[i])
        variations.append({
            'type': f'partial_missing_{criterion["criterion"].lower().replace(" ", "_")}',
            'answer': partial_answer,
            'expected_score': rubric['max_score'] - criterion['points']
        })
        
    weak_answer = generate_weak_answer(question, rubric)
    variations.append({
        'type': 'weak',
        'answer': weak_answer,
        'expected_score': rubric['max_score'] * 0.3
    })
    
    incorrect_answer = generate_incorrect_answer(question, rubric)
    variations.append({
        'type': 'incorrect',
        'answer': incorrect_answer,
        'expected_score': 0
    })
    
    return variations

def generate_perfect_answer(question: str, rubric: dict) -> str:
    """Generate a perfect answer that meets all rubric criteria"""
    answer_parts = []
    
    for criterion in rubric['criteria']:
        if "Classes & Objects" in rubric['topic']:
            if "constructor" in criterion['criterion'].lower():
                answer_parts.append("A constructor is a special member function that is automatically called when an object is created. It initializes the object's data members and can be overloaded with different parameters.")
            elif "class definition" in criterion['criterion'].lower():
                answer_parts.append("A class definition includes data members (attributes) and member functions (methods). It serves as a blueprint for creating objects.")
            elif "access specifiers" in criterion['criterion'].lower():
                answer_parts.append("Access specifiers like public, private, and protected control the visibility and accessibility of class members.")
        
        elif "Pointers & Memory" in rubric['topic']:
            if "pointer declaration" in criterion['criterion'].lower():
                answer_parts.append("A pointer is a variable that stores the memory address of another variable. It is declared using the * operator and can be initialized with the address of another variable using the & operator.")
            elif "dereferencing" in criterion['criterion'].lower():
                answer_parts.append("Dereferencing a pointer means accessing the value stored at the memory address it points to, done using the * operator.")
            elif "memory management" in criterion['criterion'].lower():
                answer_parts.append("Memory management involves allocating and deallocating memory dynamically using operators like new and delete in C++.")
        
        elif "Functions & Scope" in rubric['topic']:
            if "function definition" in criterion['criterion'].lower():
                answer_parts.append("A function definition includes the return type, function name, parameter list, and function body. It specifies what the function does when called.")
            elif "variable scope" in criterion['criterion'].lower():
                answer_parts.append("Variable scope determines where a variable can be accessed. Local variables are declared inside functions and have limited scope, while global variables are accessible throughout the program.")
            elif "function overloading" in criterion['criterion'].lower():
                answer_parts.append("Function overloading allows multiple functions with the same name but different parameter lists, enabling different behaviors based on the arguments passed.")
    
    return " ".join(answer_parts)

def generate_partial_answer(question: str, rubric: dict, exclude_criteria: list) -> str:
    """Generate a partial answer that meets some but not all criteria"""
    answer_parts = []
    
    for i, criterion in enumerate(rubric['criteria']):
        if i not in exclude_criteria:
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

def generate_weak_answer(question: str, rubric: dict) -> str:
    """Generate a weak answer with minimal understanding"""
    if "Classes & Objects" in rubric['topic']:
        return "A class is like a template for objects. It can have functions and data."
    elif "Pointers & Memory" in rubric['topic']:
        return "A pointer points to something in memory. You can use it to access data."
    elif "Functions & Scope" in rubric['topic']:
        return "Functions are blocks of code that do something. Variables can be local or global."
    else:
        return "This is related to programming concepts."

def generate_incorrect_answer(question: str, rubric: dict) -> str:
    """Generate an incorrect answer with wrong concepts"""
    if "Classes & Objects" in rubric['topic']:
        return "A class is the same as a function. You can only have one constructor and it must be public."
    elif "Pointers & Memory" in rubric['topic']:
        return "A pointer is just another variable type like int. You don't need to worry about memory management."
    elif "Functions & Scope" in rubric['topic']:
        return "Functions are only for mathematical calculations. All variables should be global for easy access."
    else:
        return "This concept is not important in programming." 