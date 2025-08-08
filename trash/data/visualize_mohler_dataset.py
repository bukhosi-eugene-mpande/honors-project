#!/usr/bin/env python3
"""
Mohler Dataset Visualization Script
===================================

This script creates comprehensive visualizations for the educational assessment dataset.
The dataset contains student answers to programming/CS questions with scoring data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_clean_data(file_path):
    """Load and clean the dataset"""
    df = pd.read_csv(file_path)
    
    # Extract topic from question ID (e.g., "1" from "1.1")
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

def create_score_distribution_plots(df):
    """Create score distribution visualizations"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Score Distribution Analysis', fontsize=16, fontweight='bold')
    
    # 1. Overall score distribution
    axes[0, 0].hist(df['score_avg'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('Distribution of Average Scores')
    axes[0, 0].set_xlabel('Average Score')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].axvline(df['score_avg'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["score_avg"].mean():.2f}')
    axes[0, 0].legend()
    
    # 2. Score comparison between evaluators
    axes[0, 1].scatter(df['score_me'], df['score_other'], alpha=0.6, color='green')
    axes[0, 1].plot([0, 5], [0, 5], 'r--', alpha=0.8, label='Perfect Agreement')
    axes[0, 1].set_title('Score Agreement Between Evaluators')
    axes[0, 1].set_xlabel('Score (Evaluator 1)')
    axes[0, 1].set_ylabel('Score (Evaluator 2)')
    axes[0, 1].legend()
    
    # 3. Score by topic
    topic_scores = df.groupby('topic_name')['score_avg'].mean().sort_values(ascending=True)
    axes[1, 0].barh(range(len(topic_scores)), topic_scores.values, color='lightcoral')
    axes[1, 0].set_yticks(range(len(topic_scores)))
    axes[1, 0].set_yticklabels(topic_scores.index, fontsize=8)
    axes[1, 0].set_title('Average Score by Topic')
    axes[1, 0].set_xlabel('Average Score')
    
    # 4. Score difference between evaluators
    df['score_diff'] = abs(df['score_me'] - df['score_other'])
    axes[1, 1].hist(df['score_diff'], bins=6, alpha=0.7, color='gold', edgecolor='black')
    axes[1, 1].set_title('Distribution of Score Differences')
    axes[1, 1].set_xlabel('Absolute Score Difference')
    axes[1, 1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('data/score_distribution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_topic_analysis(df):
    """Create topic-specific analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Topic Analysis', fontsize=16, fontweight='bold')
    
    # 1. Questions per topic
    topic_counts = df['topic_name'].value_counts()
    axes[0, 0].pie(topic_counts.values, labels=topic_counts.index, autopct='%1.1f%%', 
                   startangle=90, textprops={'fontsize': 8})
    axes[0, 0].set_title('Distribution of Questions by Topic')
    
    # 2. Score variability by topic
    topic_stats = df.groupby('topic_name').agg({
        'score_avg': ['mean', 'std', 'count']
    }).round(2)
    topic_stats.columns = ['Mean', 'Std', 'Count']
    
    axes[0, 1].bar(range(len(topic_stats)), topic_stats['Mean'], 
                   yerr=topic_stats['Std'], capsize=5, color='lightblue', alpha=0.7)
    axes[0, 1].set_xticks(range(len(topic_stats)))
    axes[0, 1].set_xticklabels(topic_stats.index, rotation=45, ha='right', fontsize=8)
    axes[0, 1].set_title('Mean Score by Topic (with Standard Deviation)')
    axes[0, 1].set_ylabel('Average Score')
    
    # 3. Score range by topic
    topic_ranges = df.groupby('topic_name')['score_avg'].agg(['min', 'max'])
    topic_ranges['range'] = topic_ranges['max'] - topic_ranges['min']
    
    axes[1, 0].bar(range(len(topic_ranges)), topic_ranges['range'], color='orange', alpha=0.7)
    axes[1, 0].set_xticks(range(len(topic_ranges)))
    axes[1, 0].set_xticklabels(topic_ranges.index, rotation=45, ha='right', fontsize=8)
    axes[1, 0].set_title('Score Range by Topic')
    axes[1, 0].set_ylabel('Score Range (Max - Min)')
    
    # 4. Box plot of scores by topic
    df.boxplot(column='score_avg', by='topic_name', ax=axes[1, 1], rot=45)
    axes[1, 1].set_title('Score Distribution by Topic')
    axes[1, 1].set_xlabel('Topic')
    axes[1, 1].set_ylabel('Average Score')
    
    plt.tight_layout()
    plt.savefig('data/topic_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_question_difficulty_analysis(df):
    """Analyze question difficulty based on scores"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Question Difficulty Analysis', fontsize=16, fontweight='bold')
    
    # 1. Easiest vs hardest questions
    question_difficulty = df.nlargest(10, 'score_avg')[['id', 'question', 'score_avg']]
    question_difficulty_hard = df.nsmallest(10, 'score_avg')[['id', 'question', 'score_avg']]
    
    # Plot easiest questions
    axes[0, 0].barh(range(len(question_difficulty)), question_difficulty['score_avg'], 
                    color='lightgreen', alpha=0.7)
    axes[0, 0].set_yticks(range(len(question_difficulty)))
    axes[0, 0].set_yticklabels(question_difficulty['id'], fontsize=8)
    axes[0, 0].set_title('Top 10 Easiest Questions')
    axes[0, 0].set_xlabel('Average Score')
    
    # Plot hardest questions
    axes[0, 1].barh(range(len(question_difficulty_hard)), question_difficulty_hard['score_avg'], 
                    color='lightcoral', alpha=0.7)
    axes[0, 1].set_yticks(range(len(question_difficulty_hard)))
    axes[0, 1].set_yticklabels(question_difficulty_hard['id'], fontsize=8)
    axes[0, 1].set_title('Top 10 Hardest Questions')
    axes[0, 1].set_xlabel('Average Score')
    
    # 2. Score distribution by question ID
    axes[1, 0].scatter(range(len(df)), df['score_avg'], alpha=0.6, color='purple')
    axes[1, 0].set_title('Score Distribution by Question Order')
    axes[1, 0].set_xlabel('Question Index')
    axes[1, 0].set_ylabel('Average Score')
    axes[1, 0].axhline(df['score_avg'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["score_avg"].mean():.2f}')
    axes[1, 0].legend()
    
    # 3. Score correlation with question length
    df['question_length'] = df['question'].str.len()
    df['answer_length'] = df['student_answer'].str.len()
    
    axes[1, 1].scatter(df['question_length'], df['score_avg'], alpha=0.6, color='teal')
    axes[1, 1].set_title('Score vs Question Length')
    axes[1, 1].set_xlabel('Question Length (characters)')
    axes[1, 1].set_ylabel('Average Score')
    
    # Add trend line
    z = np.polyfit(df['question_length'], df['score_avg'], 1)
    p = np.poly1d(z)
    axes[1, 1].plot(df['question_length'], p(df['question_length']), "r--", alpha=0.8)
    
    plt.tight_layout()
    plt.savefig('data/question_difficulty_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_text_analysis(df):
    """Analyze text patterns in questions and answers"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Text Analysis', fontsize=16, fontweight='bold')
    
    # 1. Answer length distribution
    df['answer_length'] = df['student_answer'].str.len()
    axes[0, 0].hist(df['answer_length'], bins=15, alpha=0.7, color='lightblue', edgecolor='black')
    axes[0, 0].set_title('Distribution of Student Answer Lengths')
    axes[0, 0].set_xlabel('Answer Length (characters)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].axvline(df['answer_length'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["answer_length"].mean():.0f}')
    axes[0, 0].legend()
    
    # 2. Score vs answer length
    axes[0, 1].scatter(df['answer_length'], df['score_avg'], alpha=0.6, color='orange')
    axes[0, 1].set_title('Score vs Answer Length')
    axes[0, 1].set_xlabel('Answer Length (characters)')
    axes[0, 1].set_ylabel('Average Score')
    
    # Add trend line
    z = np.polyfit(df['answer_length'], df['score_avg'], 1)
    p = np.poly1d(z)
    axes[0, 1].plot(df['answer_length'], p(df['answer_length']), "r--", alpha=0.8)
    
    # 3. Word count analysis
    df['word_count'] = df['student_answer'].str.split().str.len()
    axes[1, 0].scatter(df['word_count'], df['score_avg'], alpha=0.6, color='green')
    axes[1, 0].set_title('Score vs Word Count')
    axes[1, 0].set_xlabel('Word Count')
    axes[1, 0].set_ylabel('Average Score')
    
    # 4. Score distribution by answer length categories
    df['length_category'] = pd.cut(df['answer_length'], 
                                  bins=[0, 100, 200, 300, 500, 1000], 
                                  labels=['0-100', '100-200', '200-300', '300-500', '500+'])
    
    length_scores = df.groupby('length_category')['score_avg'].mean()
    axes[1, 1].bar(range(len(length_scores)), length_scores.values, color='purple', alpha=0.7)
    axes[1, 1].set_xticks(range(len(length_scores)))
    axes[1, 1].set_xticklabels(length_scores.index)
    axes[1, 1].set_title('Average Score by Answer Length Category')
    axes[1, 1].set_ylabel('Average Score')
    
    plt.tight_layout()
    plt.savefig('data/text_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_summary_statistics(df):
    """Create a summary statistics table"""
    print("\n" + "="*80)
    print("DATASET SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\nDataset Overview:")
    print(f"Total questions: {len(df)}")
    print(f"Total topics: {df['topic'].nunique()}")
    print(f"Date range: {df['id'].min()} to {df['id'].max()}")
    
    print(f"\nScore Statistics:")
    print(f"Average score: {df['score_avg'].mean():.2f}")
    print(f"Score standard deviation: {df['score_avg'].std():.2f}")
    print(f"Score range: {df['score_avg'].min():.1f} - {df['score_avg'].max():.1f}")
    print(f"Median score: {df['score_avg'].median():.2f}")
    
    print(f"\nEvaluator Agreement:")
    correlation = df['score_me'].corr(df['score_other'])
    print(f"Correlation between evaluators: {correlation:.3f}")
    print(f"Mean absolute difference: {df['score_diff'].mean():.2f}")
    
    print(f"\nTopic Performance (Top 5):")
    topic_performance = df.groupby('topic_name')['score_avg'].mean().sort_values(ascending=False)
    for topic, score in topic_performance.head().items():
        print(f"  {topic}: {score:.2f}")
    
    print(f"\nTopic Performance (Bottom 5):")
    for topic, score in topic_performance.tail().items():
        print(f"  {topic}: {score:.2f}")

def main():
    """Main function to run all visualizations"""
    print("Loading and analyzing Mohler dataset...")
    
    # Load data
    df = load_and_clean_data('data/mohler_dataset_edited.csv')
    
    # Create visualizations
    print("Creating score distribution plots...")
    create_score_distribution_plots(df)
    
    print("Creating topic analysis...")
    create_topic_analysis(df)
    
    print("Creating question difficulty analysis...")
    create_question_difficulty_analysis(df)
    
    print("Creating text analysis...")
    create_text_analysis(df)
    
    # Print summary statistics
    create_summary_statistics(df)
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE!")
    print("="*80)
    print("Generated files:")
    print("- score_distribution_analysis.png")
    print("- topic_analysis.png") 
    print("- question_difficulty_analysis.png")
    print("- text_analysis.png")
    print("\nThe visualizations provide insights into:")
    print("• Score distributions and evaluator agreement")
    print("• Topic-wise performance analysis")
    print("• Question difficulty patterns")
    print("• Text-based correlations with scores")

if __name__ == "__main__":
    main() 