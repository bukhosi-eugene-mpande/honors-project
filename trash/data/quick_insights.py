#!/usr/bin/env python3
"""
Quick Insights from Mohler Dataset
==================================

This script provides quick insights and analysis of the educational assessment data.
"""

import pandas as pd
import numpy as np

def load_data():
    """Load the dataset"""
    df = pd.read_csv('mohler_dataset_edited.csv')
    df['id'] = df['id'].astype(str)
    df['topic'] = df['id'].str.split('.').str[0].astype(int)
    
    # Create topic labels
    topic_labels = {
        1: "Problem Solving & Life Cycle",
        2: "Classes & Objects", 
        3: "Functions & Scope",
        4: "Arrays & Strings",
        5: "Sorting Algorithms",
        6: "Pointers & Memory",
        7: "Linked Lists",
        8: "Stacks",
        9: "Queues", 
        10: "Trees",
        11: "Object-Oriented Programming",
        12: "Data Structures & Algorithms"
    }
    df['topic_name'] = df['topic'].map(topic_labels)
    
    return df

def analyze_hardest_questions(df):
    """Find and analyze the hardest questions"""
    print("\n🔍 HARDEST QUESTIONS ANALYSIS")
    print("=" * 50)
    
    hardest = df.nsmallest(10, 'score_avg')[['id', 'question', 'score_avg', 'topic_name']]
    
    for i, (_, row) in enumerate(hardest.iterrows(), 1):
        print(f"\n{i}. Question {row['id']} ({row['topic_name']}) - Score: {row['score_avg']:.1f}")
        print(f"   Q: {row['question'][:100]}...")
        
        # Find the specific question details
        full_question = df[df['id'] == row['id']].iloc[0]
        print(f"   Expected: {full_question['desired_answer'][:80]}...")
        print(f"   Student: {full_question['student_answer'][:80]}...")

def analyze_evaluator_agreement(df):
    """Analyze evaluator agreement patterns"""
    print("\n🤝 EVALUATOR AGREEMENT ANALYSIS")
    print("=" * 50)
    
    df['score_diff'] = abs(df['score_me'] - df['score_other'])
    df['agreement_level'] = pd.cut(df['score_diff'], 
                                  bins=[0, 0.5, 1.5, 2.5, 5], 
                                  labels=['Perfect', 'Good', 'Moderate', 'Poor'])
    
    agreement_counts = df['agreement_level'].value_counts()
    print("Agreement Distribution:")
    for level, count in agreement_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {level}: {count} questions ({percentage:.1f}%)")
    
    # Find questions with highest disagreement
    high_disagreement = df.nlargest(5, 'score_diff')[['id', 'question', 'score_me', 'score_other', 'score_diff']]
    print(f"\nQuestions with Highest Evaluator Disagreement:")
    for _, row in high_disagreement.iterrows():
        print(f"  Q{row['id']}: Evaluator 1 gave {row['score_me']}, Evaluator 2 gave {row['score_other']} (diff: {row['score_diff']:.1f})")

def analyze_topic_difficulty(df):
    """Analyze topic difficulty patterns"""
    print("\n📚 TOPIC DIFFICULTY ANALYSIS")
    print("=" * 50)
    
    topic_stats = df.groupby('topic_name').agg({
        'score_avg': ['mean', 'std', 'count', 'min', 'max']
    }).round(2)
    
    topic_stats.columns = ['Mean', 'Std', 'Count', 'Min', 'Max']
    topic_stats = topic_stats.sort_values('Mean')
    
    print("Topics ranked by difficulty (easiest to hardest):")
    for i, (topic, stats) in enumerate(topic_stats.iterrows(), 1):
        print(f"  {i:2d}. {topic}: {stats['Mean']:.2f} ± {stats['Std']:.2f} (range: {stats['Min']:.1f}-{stats['Max']:.1f})")

def analyze_answer_patterns(df):
    """Analyze patterns in student answers"""
    print("\n📝 ANSWER PATTERN ANALYSIS")
    print("=" * 50)
    
    df['answer_length'] = df['student_answer'].str.len()
    df['word_count'] = df['student_answer'].str.split().str.len()
    
    # Analyze correlation between answer length and score
    length_corr = df['answer_length'].corr(df['score_avg'])
    word_corr = df['word_count'].corr(df['score_avg'])
    
    print(f"Correlation between answer length and score: {length_corr:.3f}")
    print(f"Correlation between word count and score: {word_corr:.3f}")
    
    # Find questions where longer answers got higher scores
    df['length_score_corr'] = df['answer_length'] * df['score_avg']
    high_length_high_score = df.nlargest(5, 'length_score_corr')[['id', 'answer_length', 'score_avg']]
    
    print(f"\nQuestions where longer answers correlated with higher scores:")
    for _, row in high_length_high_score.iterrows():
        print(f"  Q{row['id']}: {row['answer_length']} chars, score {row['score_avg']:.1f}")

def main():
    """Run all analyses"""
    print("🚀 Loading Mohler dataset for quick insights...")
    df = load_data()
    
    print(f"\n📊 Dataset loaded: {len(df)} questions across {df['topic'].nunique()} topics")
    
    # Run analyses
    analyze_hardest_questions(df)
    analyze_evaluator_agreement(df)
    analyze_topic_difficulty(df)
    analyze_answer_patterns(df)
    
    print("\n" + "=" * 50)
    print("✅ QUICK INSIGHTS COMPLETE!")
    print("=" * 50)
    print("\nKey takeaways:")
    print("• Use the full visualization script for detailed charts")
    print("• Focus on topics with lowest scores for curriculum improvement")
    print("• Consider evaluator training for questions with high disagreement")
    print("• Analyze answer patterns to understand student thinking")

if __name__ == "__main__":
    main() 