#!/usr/bin/env python3
"""
Local Pipeline Demo
===================

This script demonstrates the rubric assessment pipeline locally without AWS dependencies.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import matplotlib.pyplot as plt
import seaborn as sns

class LocalRubricAssessmentPipeline:
    """Local version of the rubric assessment pipeline for demonstration"""
    
    def __init__(self):
        self.pipeline_id = str(uuid.uuid4())
        self.results = {}
        
    def create_rubric_template(self, topic: str, criteria: list) -> dict:
        """Create a rubric template for a specific topic"""
        return {
            "topic": topic,
            "criteria": criteria,
            "max_score": sum(criterion["points"] for criterion in criteria),
            "created_at": datetime.now().isoformat(),
            "rubric_id": str(uuid.uuid4())
        }
    
    def generate_sample_rubrics(self) -> dict:
        """Generate sample rubrics for programming topics"""
        rubrics = {}
        
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
    
    def generate_answer_variations(self, question: str, rubric: dict) -> list:
        """Generate multiple answer variations based on rubric criteria"""
        variations = []
        
        perfect_answer = self._generate_perfect_answer(question, rubric)
        variations.append({
            'type': 'perfect',
            'answer': perfect_answer,
            'expected_score': rubric['max_score']
        })
        
        for i, criterion in enumerate(rubric['criteria']):
            partial_answer = self._generate_partial_answer(question, rubric, exclude_criteria=[i])
            variations.append({
                'type': f'partial_missing_{criterion["criterion"].lower().replace(" ", "_")}',
                'answer': partial_answer,
                'expected_score': rubric['max_score'] - criterion['points']
            })
        
        weak_answer = self._generate_weak_answer(question, rubric)
        variations.append({
            'type': 'weak',
            'answer': weak_answer,
            'expected_score': rubric['max_score'] * 0.3
        })
        
        incorrect_answer = self._generate_incorrect_answer(question, rubric)
        variations.append({
            'type': 'incorrect',
            'answer': incorrect_answer,
            'expected_score': 0
        })
        
        return variations
    
    def _generate_perfect_answer(self, question: str, rubric: dict) -> str:
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
    
    def _generate_partial_answer(self, question: str, rubric: dict, exclude_criteria: list) -> str:
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
    
    def _generate_weak_answer(self, question: str, rubric: dict) -> str:
        """Generate a weak answer with minimal understanding"""
        if "Classes & Objects" in rubric['topic']:
            return "A class is like a template for objects. It can have functions and data."
        elif "Pointers & Memory" in rubric['topic']:
            return "A pointer points to something in memory. You can use it to access data."
        elif "Functions & Scope" in rubric['topic']:
            return "Functions are blocks of code that do something. Variables can be local or global."
        else:
            return "This is related to programming concepts."
    
    def _generate_incorrect_answer(self, question: str, rubric: dict) -> str:
        """Generate an incorrect answer with wrong concepts"""
        if "Classes & Objects" in rubric['topic']:
            return "A class is the same as a function. You can only have one constructor and it must be public."
        elif "Pointers & Memory" in rubric['topic']:
            return "A pointer is just another variable type like int. You don't need to worry about memory management."
        elif "Functions & Scope" in rubric['topic']:
            return "Functions are only for mathematical calculations. All variables should be global for easy access."
        else:
            return "This concept is not important in programming."
    
    def assess_answer_with_nlp(self, answer: str, rubric: dict) -> dict:
        """Assess an answer using NLP techniques (local implementation)"""
        assessment = {
            "answer": answer,
            "criteria_scores": [],
            "total_score": 0,
            "nlp_analysis": {}
        }
        
        keyword_scores = self._analyze_keywords(answer, rubric)
        
        sentiment = self._analyze_sentiment(answer)
        
        complexity = self._analyze_complexity(answer)
        
        semantic_similarity = self._analyze_semantic_similarity(answer, rubric)
        
        for criterion in rubric['criteria']:
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
    
    def _analyze_keywords(self, answer: str, rubric: dict) -> dict:
        """Analyze keyword presence in the answer"""
        keyword_scores = {}
        
        for criterion in rubric['criteria']:
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
    
    def _analyze_sentiment(self, answer: str) -> dict:
        """Analyze sentiment of the answer"""
        positive_words = ["correct", "proper", "good", "right", "accurate", "clear", "understand", "know"]
        negative_words = ["wrong", "incorrect", "bad", "confused", "unclear", "don't", "not"]
        
        words = answer.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            score = min(1.0, positive_count / (positive_count + negative_count + 1))
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            score = max(0.0, 1 - (negative_count / (positive_count + negative_count + 1)))
        else:
            sentiment = "NEUTRAL"
            score = 0.5
        
        return {"sentiment": sentiment, "score": score}
    
    def _analyze_complexity(self, answer: str) -> dict:
        """Analyze text complexity"""
        words = answer.split()
        sentences = answer.split('.')
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        unique_words = len(set(words))
        lexical_diversity = unique_words / len(words) if words else 0
        
        complexity_score = min(1.0, (avg_sentence_length / 20) * 0.5 + lexical_diversity * 0.5)
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "lexical_diversity": lexical_diversity,
            "complexity_score": complexity_score
        }
    
    def _analyze_semantic_similarity(self, answer: str, rubric: dict) -> dict:
        """Analyze semantic similarity to expected concepts"""
        expected_concepts = []
        for criterion in rubric['criteria']:
            expected_concepts.extend(criterion["keywords"])
        
        answer_words = set(answer.lower().split())
        expected_words = set([word.lower() for word in expected_concepts])
        
        overlap = len(answer_words.intersection(expected_words))
        similarity = overlap / len(expected_words) if expected_words else 0
        
        return {"similarity_score": similarity, "concept_overlap": overlap}
    
    def _score_criterion(self, answer: str, criterion: dict, keyword_scores: dict, 
                        sentiment: dict, complexity: dict, semantic_similarity: dict) -> float:
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
    
    def _generate_feedback(self, score: float, criterion: dict) -> str:
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
    
    def run_pipeline_demo(self):
        """Run the complete pipeline demonstration"""
        print(" Starting Rubric Assessment Pipeline Demo")
        print("=" * 60)
        
        print("\n Step 1: Initializing Pipeline")
        print(f"Pipeline ID: {self.pipeline_id}")
        print("Pipeline initialized successfully")
        
        print("\n Step 2: Loading Rubrics")
        rubrics = self.generate_sample_rubrics()
        print(f" Loaded {len(rubrics)} rubrics:")
        for topic, rubric in rubrics.items():
            print(f"   - {rubric['topic']} ({len(rubric['criteria'])} criteria, {rubric['max_score']} points)")
        
        print("\n Step 3: Generating Answer Variations")
        sample_questions = {
            "classes_objects": "What is a constructor and how is it used in object-oriented programming?",
            "pointers_memory": "What is a pointer and how do you declare one?",
            "functions_scope": "How do you define a function in C++?"
        }
        
        all_variations = {}
        for topic_key, question in sample_questions.items():
            rubric = rubrics[topic_key]
            variations = self.generate_answer_variations(question, rubric)
            all_variations[topic_key] = {
                'question': question,
                'variations': variations
            }
            print(f"   - {topic_key}: Generated {len(variations)} answer variations")
        
        print("\n Step 4: Performing NLP Assessment")
        assessment_results = {}
        
        for topic_key, data in all_variations.items():
            question = data['question']
            variations = data['variations']
            rubric = rubrics[topic_key]
            
            topic_results = []
            for variation in variations:
                assessment = self.assess_answer_with_nlp(variation['answer'], rubric)
                topic_results.append({
                    'type': variation['type'],
                    'answer': variation['answer'][:100] + "..." if len(variation['answer']) > 100 else variation['answer'],
                    'expected_score': variation['expected_score'],
                    'actual_score': assessment['total_score'],
                    'nlp_analysis': assessment['nlp_analysis']
                })
            
            assessment_results[topic_key] = topic_results
            avg_score = np.mean([r['actual_score'] for r in topic_results])
            print(f"   - {topic_key}: Average score {avg_score:.2f}/{rubric['max_score']}")
        
        print("\n Step 5: Score Calculation and Analysis")
        
        all_scores = []
        all_sentiments = []
        all_complexities = []
        
        for topic_results in assessment_results.values():
            for result in topic_results:
                all_scores.append(result['actual_score'])
                all_sentiments.append(result['nlp_analysis']['sentiment']['sentiment'])
                all_complexities.append(result['nlp_analysis']['complexity']['complexity_score'])
        
        print(f"   - Total assessments: {len(all_scores)}")
        print(f"   - Average score: {np.mean(all_scores):.2f}")
        print(f"   - Score range: {min(all_scores):.2f} - {max(all_scores):.2f}")
        
        sentiment_counts = pd.Series(all_sentiments).value_counts()
        sentiment_dict = {str(k): int(v) for k, v in sentiment_counts.items()}
        print(f"   - Sentiment distribution: {sentiment_dict}")
        
        print("\nStep 6: Generating Report")
        
        report = {
            'pipeline_id': self.pipeline_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_assessments': len(all_scores),
                'average_score': float(np.mean(all_scores)),
                'score_std': float(np.std(all_scores)),
                'topics_covered': len(rubrics),
                'sentiment_distribution': sentiment_dict
            },
            'detailed_results': assessment_results
        }
        
        with open('pipeline_demo_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(" Report generated: pipeline_demo_report.json")
        
        print("\n Step 7: Creating Visualizations")
        self._create_demo_visualizations(assessment_results, all_scores, all_sentiments)
        
        print("\n Pipeline Demo Completed Successfully!")
        print("=" * 60)
        print("Generated files:")
        print("- pipeline_demo_report.json")
        print("- demo_score_distribution.png")
        print("- demo_sentiment_analysis.png")
        print("- demo_topic_performance.png")
        
        return report
    
    def _create_demo_visualizations(self, assessment_results, all_scores, all_sentiments):
        """Create visualizations for the demo"""
        
        # 1. Score Distribution
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        plt.hist(all_scores, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Score Distribution')
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.axvline(np.mean(all_scores), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(all_scores):.2f}')
        plt.legend()
        
        # 2. Sentiment Analysis
        plt.subplot(2, 2, 2)
        sentiment_counts = pd.Series(all_sentiments).value_counts()
        plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
        plt.title('Sentiment Distribution')
        
        # 3. Topic Performance
        plt.subplot(2, 2, 3)
        topic_avg_scores = []
        topic_names = []
        
        for topic_key, results in assessment_results.items():
            avg_score = np.mean([r['actual_score'] for r in results])
            topic_avg_scores.append(avg_score)
            topic_names.append(topic_key.replace('_', ' ').title())
        
        bars = plt.bar(topic_names, topic_avg_scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.title('Average Score by Topic')
        plt.ylabel('Average Score')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, score in zip(bars, topic_avg_scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{score:.2f}', ha='center', va='bottom')
        
        # 4. Answer Type Performance
        plt.subplot(2, 2, 4)
        answer_types = []
        type_scores = []
        
        for topic_results in assessment_results.values():
            for result in topic_results:
                answer_types.append(result['type'])
                type_scores.append(result['actual_score'])
        
        df_types = pd.DataFrame({'type': answer_types, 'score': type_scores})
        type_avg = df_types.groupby('type')['score'].mean()
        
        bars = plt.bar(range(len(type_avg)), type_avg.values, color='orange', alpha=0.7)
        plt.xticks(range(len(type_avg)), type_avg.index, rotation=45, ha='right')
        plt.title('Performance by Answer Type')
        plt.ylabel('Average Score')
        
        plt.tight_layout()
        plt.savefig('demo_score_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create additional visualizations
        self._create_sentiment_analysis_plot(all_sentiments)
        self._create_topic_performance_plot(assessment_results)
    
    def _create_sentiment_analysis_plot(self, all_sentiments):
        """Create detailed sentiment analysis plot"""
        plt.figure(figsize=(12, 8))
        
        sentiment_counts = pd.Series(all_sentiments).value_counts()
        colors = ['#2E8B57', '#CD5C5C', '#4682B4']
        
        plt.pie(sentiment_counts.values, labels=sentiment_counts.index, 
               autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Detailed Sentiment Analysis of Generated Answers', fontsize=14, fontweight='bold')
        
        plt.savefig('demo_sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _create_topic_performance_plot(self, assessment_results):
        """Create detailed topic performance plot"""
        plt.figure(figsize=(14, 8))
        
        topics = []
        perfect_scores = []
        partial_scores = []
        weak_scores = []
        incorrect_scores = []
        
        for topic_key, results in assessment_results.items():
            topics.append(topic_key.replace('_', ' ').title())
            
            perfect = [r['actual_score'] for r in results if r['type'] == 'perfect']
            partial = [r['actual_score'] for r in results if 'partial' in r['type']]
            weak = [r['actual_score'] for r in results if r['type'] == 'weak']
            incorrect = [r['actual_score'] for r in results if r['type'] == 'incorrect']
            
            perfect_scores.append(np.mean(perfect) if perfect else 0)
            partial_scores.append(np.mean(partial) if partial else 0)
            weak_scores.append(np.mean(weak) if weak else 0)
            incorrect_scores.append(np.mean(incorrect) if incorrect else 0)
        
        x = np.arange(len(topics))
        width = 0.2
        
        plt.bar(x - 1.5*width, perfect_scores, width, label='Perfect', color='#2E8B57')
        plt.bar(x - 0.5*width, partial_scores, width, label='Partial', color='#4682B4')
        plt.bar(x + 0.5*width, weak_scores, width, label='Weak', color='#FFD700')
        plt.bar(x + 1.5*width, incorrect_scores, width, label='Incorrect', color='#CD5C5C')
        
        plt.xlabel('Topics')
        plt.ylabel('Average Score')
        plt.title('Detailed Topic Performance by Answer Type', fontsize=14, fontweight='bold')
        plt.xticks(x, topics)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('demo_topic_performance.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main function to run the local pipeline demo"""
    print("🎓 Rubric Assessment Pipeline - Local Demo")
    print("=" * 60)
    
    # Initialize and run pipeline
    pipeline = LocalRubricAssessmentPipeline()
    results = pipeline.run_pipeline_demo()
    
    # Display summary
    print("\n Final Summary:")
    print(f"Pipeline ID: {results['pipeline_id']}")
    print(f"Total Assessments: {results['summary']['total_assessments']}")
    print(f"Average Score: {results['summary']['average_score']:.2f}")
    print(f"Topics Covered: {results['summary']['topics_covered']}")
    print(f"Sentiment Distribution: {results['summary']['sentiment_distribution']}")

if __name__ == "__main__":
    main() 