#!/usr/bin/env python3
"""
Rubric-Based Assessment Pipeline
================================

This script defines a comprehensive pipeline for automated assessment using rubrics
and NLP techniques. It includes AWS Step Functions definition and visualization.
"""

import json
import boto3
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import uuid

class RubricAssessmentPipeline:
    """Main pipeline class for rubric-based assessment"""
    
    def __init__(self):
        self.step_functions = boto3.client('stepfunctions')
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.sagemaker = boto3.client('sagemaker')
        
    def create_rubric_template(self, topic: str, criteria: List[Dict]) -> Dict:
        """Create a rubric template for a specific topic"""
        return {
            "topic": topic,
            "criteria": criteria,
            "max_score": sum(criterion["points"] for criterion in criteria),
            "created_at": datetime.now().isoformat(),
            "rubric_id": str(uuid.uuid4())
        }
    
    def generate_sample_rubrics(self) -> Dict[str, Dict]:
        """Generate sample rubrics for programming topics"""
        rubrics = {}
        
        # Classes & Objects Rubric
        rubrics["classes_objects"] = self.create_rubric_template(
            "Classes & Objects",
            [
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
            ]
        )
        
        # Pointers & Memory Rubric
        rubrics["pointers_memory"] = self.create_rubric_template(
            "Pointers & Memory",
            [
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
            ]
        )
        
        # Functions & Scope Rubric
        rubrics["functions_scope"] = self.create_rubric_template(
            "Functions & Scope",
            [
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
            ]
        )
        
        return rubrics
    
    def generate_answer_variations(self, question: str, rubric: Dict) -> List[str]:
        """Generate multiple answer variations based on rubric criteria"""
        variations = []
        
        # Perfect answer (all criteria met)
        perfect_answer = self._generate_perfect_answer(question, rubric)
        variations.append(perfect_answer)
        
        # Partial answers (some criteria met)
        for i, criterion in enumerate(rubric["criteria"]):
            partial_answer = self._generate_partial_answer(question, rubric, exclude_criteria=[i])
            variations.append(partial_answer)
        
        # Weak answer (minimal criteria met)
        weak_answer = self._generate_weak_answer(question, rubric)
        variations.append(weak_answer)
        
        # Incorrect answer (wrong concepts)
        incorrect_answer = self._generate_incorrect_answer(question, rubric)
        variations.append(incorrect_answer)
        
        return variations
    
    def _generate_perfect_answer(self, question: str, rubric: Dict) -> str:
        """Generate a perfect answer that meets all rubric criteria"""
        answer_parts = []
        
        for criterion in rubric["criteria"]:
            if "Classes & Objects" in rubric["topic"]:
                if "constructor" in criterion["criterion"].lower():
                    answer_parts.append("A constructor is a special member function that is automatically called when an object is created. It initializes the object's data members and can be overloaded with different parameters.")
                elif "class definition" in criterion["criterion"].lower():
                    answer_parts.append("A class definition includes data members (attributes) and member functions (methods). It serves as a blueprint for creating objects.")
                elif "access specifiers" in criterion["criterion"].lower():
                    answer_parts.append("Access specifiers like public, private, and protected control the visibility and accessibility of class members.")
            
            elif "Pointers & Memory" in rubric["topic"]:
                if "pointer declaration" in criterion["criterion"].lower():
                    answer_parts.append("A pointer is a variable that stores the memory address of another variable. It is declared using the * operator and can be initialized with the address of another variable using the & operator.")
                elif "dereferencing" in criterion["criterion"].lower():
                    answer_parts.append("Dereferencing a pointer means accessing the value stored at the memory address it points to, done using the * operator.")
                elif "memory management" in criterion["criterion"].lower():
                    answer_parts.append("Memory management involves allocating and deallocating memory dynamically using operators like new and delete in C++.")
            
            elif "Functions & Scope" in rubric["topic"]:
                if "function definition" in criterion["criterion"].lower():
                    answer_parts.append("A function definition includes the return type, function name, parameter list, and function body. It specifies what the function does when called.")
                elif "variable scope" in criterion["criterion"].lower():
                    answer_parts.append("Variable scope determines where a variable can be accessed. Local variables are declared inside functions and have limited scope, while global variables are accessible throughout the program.")
                elif "function overloading" in criterion["criterion"].lower():
                    answer_parts.append("Function overloading allows multiple functions with the same name but different parameter lists, enabling different behaviors based on the arguments passed.")
        
        return " ".join(answer_parts)
    
    def _generate_partial_answer(self, question: str, rubric: Dict, exclude_criteria: List[int]) -> str:
        """Generate a partial answer that meets some but not all criteria"""
        answer_parts = []
        
        for i, criterion in enumerate(rubric["criteria"]):
            if i not in exclude_criteria:
                if "Classes & Objects" in rubric["topic"]:
                    if "constructor" in criterion["criterion"].lower():
                        answer_parts.append("A constructor is called when an object is created.")
                    elif "class definition" in criterion["criterion"].lower():
                        answer_parts.append("A class has data members and functions.")
                    elif "access specifiers" in criterion["criterion"].lower():
                        answer_parts.append("There are public and private members in a class.")
                
                elif "Pointers & Memory" in rubric["topic"]:
                    if "pointer declaration" in criterion["criterion"].lower():
                        answer_parts.append("A pointer stores an address.")
                    elif "dereferencing" in criterion["criterion"].lower():
                        answer_parts.append("You use * to get the value from a pointer.")
                    elif "memory management" in criterion["criterion"].lower():
                        answer_parts.append("Memory can be allocated and freed.")
                
                elif "Functions & Scope" in rubric["topic"]:
                    if "function definition" in criterion["criterion"].lower():
                        answer_parts.append("A function has a name and parameters.")
                    elif "variable scope" in criterion["criterion"].lower():
                        answer_parts.append("Variables have different scopes.")
                    elif "function overloading" in criterion["criterion"].lower():
                        answer_parts.append("Functions can have the same name.")
        
        return " ".join(answer_parts) if answer_parts else "I don't know much about this topic."
    
    def _generate_weak_answer(self, question: str, rubric: Dict) -> str:
        """Generate a weak answer with minimal understanding"""
        if "Classes & Objects" in rubric["topic"]:
            return "A class is like a template for objects. It can have functions and data."
        elif "Pointers & Memory" in rubric["topic"]:
            return "A pointer points to something in memory. You can use it to access data."
        elif "Functions & Scope" in rubric["topic"]:
            return "Functions are blocks of code that do something. Variables can be local or global."
        else:
            return "This is related to programming concepts."
    
    def _generate_incorrect_answer(self, question: str, rubric: Dict) -> str:
        """Generate an incorrect answer with wrong concepts"""
        if "Classes & Objects" in rubric["topic"]:
            return "A class is the same as a function. You can only have one constructor and it must be public."
        elif "Pointers & Memory" in rubric["topic"]:
            return "A pointer is just another variable type like int. You don't need to worry about memory management."
        elif "Functions & Scope" in rubric["topic"]:
            return "Functions are only for mathematical calculations. All variables should be global for easy access."
        else:
            return "This concept is not important in programming."
    
    def assess_answer_with_nlp(self, answer: str, rubric: Dict) -> Dict:
        """Assess an answer using NLP techniques"""
        assessment = {
            "answer": answer,
            "criteria_scores": [],
            "total_score": 0,
            "nlp_analysis": {}
        }
        
        # Keyword matching
        keyword_scores = self._analyze_keywords(answer, rubric)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(answer)
        
        # Text complexity analysis
        complexity = self._analyze_complexity(answer)
        
        # Semantic similarity (simulated)
        semantic_similarity = self._analyze_semantic_similarity(answer, rubric)
        
        # Score each criterion
        for criterion in rubric["criteria"]:
            criterion_score = self._score_criterion(
                answer, criterion, keyword_scores, sentiment, complexity, semantic_similarity
            )
            assessment["criteria_scores"].append({
                "criterion": criterion["criterion"],
                "score": criterion_score,
                "max_score": criterion["points"],
                "feedback": self._generate_feedback(criterion_score, criterion)
            })
            assessment["total_score"] += criterion_score
        
        assessment["nlp_analysis"] = {
            "keyword_matches": keyword_scores,
            "sentiment": sentiment,
            "complexity": complexity,
            "semantic_similarity": semantic_similarity
        }
        
        return assessment
    
    def _analyze_keywords(self, answer: str, rubric: Dict) -> Dict:
        """Analyze keyword presence in the answer"""
        keyword_scores = {}
        
        for criterion in rubric["criteria"]:
            matches = 0
            total_keywords = len(criterion["keywords"])
            
            for keyword in criterion["keywords"]:
                if keyword.lower() in answer.lower():
                    matches += 1
            
            keyword_scores[criterion["criterion"]] = {
                "matches": matches,
                "total": total_keywords,
                "score": matches / total_keywords if total_keywords > 0 else 0
            }
        
        return keyword_scores
    
    def _analyze_sentiment(self, answer: str) -> Dict:
        """Analyze sentiment of the answer"""
        # Simulate sentiment analysis
        positive_words = ["correct", "proper", "good", "right", "accurate", "clear", "understand"]
        negative_words = ["wrong", "incorrect", "bad", "confused", "unclear", "don't know"]
        
        positive_count = sum(1 for word in positive_words if word in answer.lower())
        negative_count = sum(1 for word in negative_words if word in answer.lower())
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(1.0, positive_count / (positive_count + negative_count + 1))
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.0, 1 - (negative_count / (positive_count + negative_count + 1)))
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {"sentiment": sentiment, "score": score}
    
    def _analyze_complexity(self, answer: str) -> Dict:
        """Analyze text complexity"""
        words = answer.split()
        sentences = answer.split('.')
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        unique_words = len(set(words))
        lexical_diversity = unique_words / len(words) if words else 0
        
        # Complexity score based on sentence length and vocabulary
        complexity_score = min(1.0, (avg_sentence_length / 20) * 0.5 + lexical_diversity * 0.5)
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "lexical_diversity": lexical_diversity,
            "complexity_score": complexity_score
        }
    
    def _analyze_semantic_similarity(self, answer: str, rubric: Dict) -> Dict:
        """Analyze semantic similarity to expected concepts"""
        # Simulate semantic similarity analysis
        expected_concepts = []
        for criterion in rubric["criteria"]:
            expected_concepts.extend(criterion["keywords"])
        
        answer_words = set(answer.lower().split())
        expected_words = set([word.lower() for word in expected_concepts])
        
        overlap = len(answer_words.intersection(expected_words))
        similarity = overlap / len(expected_words) if expected_words else 0
        
        return {"similarity_score": similarity, "concept_overlap": overlap}
    
    def _score_criterion(self, answer: str, criterion: Dict, keyword_scores: Dict, 
                        sentiment: Dict, complexity: Dict, semantic_similarity: Dict) -> float:
        """Score a specific criterion based on multiple factors"""
        keyword_score = keyword_scores.get(criterion["criterion"], {}).get("score", 0)
        sentiment_score = sentiment.get("score", 0.5)
        complexity_score = complexity.get("complexity_score", 0.5)
        semantic_score = semantic_similarity.get("similarity_score", 0)
        
        # Weighted scoring
        final_score = (
            keyword_score * 0.4 +
            sentiment_score * 0.2 +
            complexity_score * 0.2 +
            semantic_score * 0.2
        )
        
        return min(criterion["points"], final_score * criterion["points"])
    
    def _generate_feedback(self, score: float, criterion: Dict) -> str:
        """Generate feedback based on score"""
        max_score = criterion["points"]
        percentage = score / max_score if max_score > 0 else 0
        
        if percentage >= 0.8:
            return f"Excellent understanding of {criterion['criterion'].lower()}"
        elif percentage >= 0.6:
            return f"Good understanding of {criterion['criterion'].lower()}"
        elif percentage >= 0.4:
            return f"Partial understanding of {criterion['criterion'].lower()}"
        elif percentage >= 0.2:
            return f"Limited understanding of {criterion['criterion'].lower()}"
        else:
            return f"Needs improvement in {criterion['criterion'].lower()}"
    
    def create_step_functions_definition(self) -> Dict:
        """Create AWS Step Functions definition for the pipeline"""
        return {
            "Comment": "Rubric-Based Assessment Pipeline",
            "StartAt": "InitializePipeline",
            "States": {
                "InitializePipeline": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:initialize-pipeline",
                    "Next": "LoadRubrics"
                },
                "LoadRubrics": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:load-rubrics",
                    "Next": "GenerateAnswerVariations"
                },
                "GenerateAnswerVariations": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:generate-answers",
                    "Next": "NLPAssessment"
                },
                "NLPAssessment": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:nlp-assessment",
                    "Next": "ScoreCalculation"
                },
                "ScoreCalculation": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:calculate-scores",
                    "Next": "ResultsAnalysis"
                },
                "ResultsAnalysis": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:analyze-results",
                    "Next": "GenerateReport"
                },
                "GenerateReport": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:generate-report",
                    "End": True
                }
            }
        }
    
    def visualize_pipeline(self):
        """Create a visual representation of the pipeline"""
        G = nx.DiGraph()
        
        # Add nodes
        nodes = [
            "Initialize Pipeline",
            "Load Rubrics",
            "Generate Answer Variations",
            "NLP Assessment",
            "Score Calculation",
            "Results Analysis",
            "Generate Report"
        ]
        
        for node in nodes:
            G.add_node(node)
        
        # Add edges
        edges = [
            ("Initialize Pipeline", "Load Rubrics"),
            ("Load Rubrics", "Generate Answer Variations"),
            ("Generate Answer Variations", "NLP Assessment"),
            ("NLP Assessment", "Score Calculation"),
            ("Score Calculation", "Results Analysis"),
            ("Results Analysis", "Generate Report")
        ]
        
        for edge in edges:
            G.add_edge(edge[0], edge[1])
        
        # Create visualization
        plt.figure(figsize=(16, 10))
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=3000, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title("Rubric-Based Assessment Pipeline", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('rubric_assessment_pipeline.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return G

def main():
    """Main function to demonstrate the pipeline"""
    pipeline = RubricAssessmentPipeline()
    
    # Generate sample rubrics
    rubrics = pipeline.generate_sample_rubrics()
    
    # Create Step Functions definition
    step_functions_def = pipeline.create_step_functions_definition()
    
    # Save Step Functions definition
    with open('step_functions_definition.json', 'w') as f:
        json.dump(step_functions_def, f, indent=2)
    
    # Visualize pipeline
    pipeline.visualize_pipeline()
    
    # Demonstrate assessment with sample data
    sample_question = "What is a constructor and how is it used in object-oriented programming?"
    rubric = rubrics["classes_objects"]
    
    print("Sample Assessment Demonstration:")
    print("=" * 50)
    print(f"Question: {sample_question}")
    print(f"Topic: {rubric['topic']}")
    print(f"Max Score: {rubric['max_score']}")
    
    # Generate answer variations
    variations = pipeline.generate_answer_variations(sample_question, rubric)
    
    print(f"\nGenerated {len(variations)} answer variations:")
    for i, variation in enumerate(variations, 1):
        print(f"\nVariation {i}:")
        print(f"Answer: {variation[:100]}...")
        
        # Assess the answer
        assessment = pipeline.assess_answer_with_nlp(variation, rubric)
        print(f"Score: {assessment['total_score']:.1f}/{rubric['max_score']}")
        
        for criterion_score in assessment['criteria_scores']:
            print(f"  {criterion_score['criterion']}: {criterion_score['score']:.1f}/{criterion_score['max_score']}")
    
    print("\nPipeline files generated:")
    print("- step_functions_definition.json")
    print("- rubric_assessment_pipeline.png")

if __name__ == "__main__":
    main() 