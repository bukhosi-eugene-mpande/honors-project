#!/usr/bin/env python3
"""
Mohler Dataset Visualization Script (Simplified)
================================================

This script creates comprehensive visualizations for the educational assessment dataset.
The dataset contains student answers to programming/CS questions with scoring data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_and_clean_data(file_path):
    """Load and clean the dataset"""
    df = pd.read_csv(file_path)
    
    # Ensure id column is string type
    df['id'] = df['id'].astype(str)
    
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

def create_comprehensive_analysis(df):
    """Create a comprehensive analysis dashboard"""
    fig = plt.figure(figsize=(20, 16))
    
    # Create a grid layout
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    # 1. Score distribution histogram
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.hist(df['score_avg'], bins=12, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.set_title('Distribution of Average Scores', fontweight='bold')
    ax1.set_xlabel('Average Score')
    ax1.set_ylabel('Frequency')
    ax1.axvline(df['score_avg'].mean(), color='red', linestyle='--', 
                label=f'Mean: {df["score_avg"].mean():.2f}')
    ax1.legend()
    
    # 2. Evaluator agreement scatter plot
    ax2 = fig.add_subplot(gs[0, 2:])
    ax2.scatter(df['score_me'], df['score_other'], alpha=0.6, color='green')
    ax2.plot([0, 5], [0, 5], 'r--', alpha=0.8, label='Perfect Agreement')
    ax2.set_title('Score Agreement Between Evaluators', fontweight='bold')
    ax2.set_xlabel('Score (Evaluator 1)')
    ax2.set_ylabel('Score (Evaluator 2)')
    ax2.legend()
    
    # 3. Topic performance bar chart
    ax3 = fig.add_subplot(gs[1, :])
    topic_scores = df.groupby('topic_name')['score_avg'].mean().sort_values(ascending=True)
    bars = ax3.barh(range(len(topic_scores)), topic_scores.values, color='lightcoral')
    ax3.set_yticks(range(len(topic_scores)))
    ax3.set_yticklabels(topic_scores.index, fontsize=9)
    ax3.set_title('Average Score by Topic', fontweight='bold')
    ax3.set_xlabel('Average Score')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}', ha='left', va='center', fontsize=8)
    
    # 4. Score vs answer length
    ax4 = fig.add_subplot(gs[2, :2])
    df['answer_length'] = df['student_answer'].str.len()
    ax4.scatter(df['answer_length'], df['score_avg'], alpha=0.6, color='orange')
    ax4.set_title('Score vs Answer Length', fontweight='bold')
    ax4.set_xlabel('Answer Length (characters)')
    ax4.set_ylabel('Average Score')
    
    # Add trend line
    z = np.polyfit(df['answer_length'], df['score_avg'], 1)
    p = np.poly1d(z)
    ax4.plot(df['answer_length'], p(df['answer_length']), "r--", alpha=0.8)
    
    # 5. Score difference distribution
    ax5 = fig.add_subplot(gs[2, 2:])
    df['score_diff'] = abs(df['score_me'] - df['score_other'])
    ax5.hist(df['score_diff'], bins=6, alpha=0.7, color='gold', edgecolor='black')
    ax5.set_title('Distribution of Score Differences', fontweight='bold')
    ax5.set_xlabel('Absolute Score Difference')
    ax5.set_ylabel('Frequency')
    
    # 6. Question difficulty analysis
    ax6 = fig.add_subplot(gs[3, :])
    # Get easiest and hardest questions
    easiest = df.nlargest(5, 'score_avg')[['id', 'score_avg']]
    hardest = df.nsmallest(5, 'score_avg')[['id', 'score_avg']]
    
    x_pos = np.arange(len(easiest) + len(hardest))
    scores = list(easiest['score_avg']) + list(hardest['score_avg'])
    colors = ['lightgreen'] * len(easiest) + ['lightcoral'] * len(hardest)
    labels = list(easiest['id']) + list(hardest['id'])
    
    bars = ax6.bar(x_pos, scores, color=colors, alpha=0.7)
    ax6.set_title('Easiest vs Hardest Questions', fontweight='bold')
    ax6.set_xlabel('Question ID')
    ax6.set_ylabel('Average Score')
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels(labels, rotation=45)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='lightgreen', label='Easiest'),
                      Patch(facecolor='lightcoral', label='Hardest')]
    ax6.legend(handles=legend_elements)
    
    plt.suptitle('Mohler Dataset Analysis Dashboard', fontsize=16, fontweight='bold')
    plt.savefig('mohler_analysis_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_detailed_topic_analysis(df):
    """Create detailed topic analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Detailed Topic Analysis', fontsize=16, fontweight='bold')
    
    # 1. Questions per topic
    topic_counts = df['topic_name'].value_counts()
    axes[0, 0].pie(topic_counts.values, labels=topic_counts.index, autopct='%1.1f%%', 
                   startangle=90, textprops={'fontsize': 8})
    axes[0, 0].set_title('Distribution of Questions by Topic')
    
    # 2. Score statistics by topic
    topic_stats = df.groupby('topic_name').agg({
        'score_avg': ['mean', 'std', 'count']
    }).round(2)
    topic_stats.columns = ['Mean', 'Std', 'Count']
    
    x_pos = np.arange(len(topic_stats))
    axes[0, 1].bar(x_pos, topic_stats['Mean'], yerr=topic_stats['Std'], 
                   capsize=5, color='lightblue', alpha=0.7)
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(topic_stats.index, rotation=45, ha='right', fontsize=8)
    axes[0, 1].set_title('Mean Score by Topic (with Standard Deviation)')
    axes[0, 1].set_ylabel('Average Score')
    
    # 3. Score range by topic
    topic_ranges = df.groupby('topic_name')['score_avg'].agg(['min', 'max'])
    topic_ranges['range'] = topic_ranges['max'] - topic_ranges['min']
    
    axes[1, 0].bar(x_pos, topic_ranges['range'], color='orange', alpha=0.7)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(topic_ranges.index, rotation=45, ha='right', fontsize=8)
    axes[1, 0].set_title('Score Range by Topic')
    axes[1, 0].set_ylabel('Score Range (Max - Min)')
    
    # 4. Box plot of scores by topic
    df.boxplot(column='score_avg', by='topic_name', ax=axes[1, 1], rot=45)
    axes[1, 1].set_title('Score Distribution by Topic')
    axes[1, 1].set_xlabel('Topic')
    axes[1, 1].set_ylabel('Average Score')
    
    plt.tight_layout()
    plt.savefig('detailed_topic_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_summary_statistics(df):
    """Print comprehensive summary statistics"""
    print("\n" + "="*80)
    print("MOHLER DATASET SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total questions: {len(df)}")
    print(f"   Total topics: {df['topic'].nunique()}")
    print(f"   Question range: {df['id'].min()} to {df['id'].max()}")
    
    print(f"\n📈 Score Statistics:")
    print(f"   Average score: {df['score_avg'].mean():.2f}")
    print(f"   Score standard deviation: {df['score_avg'].std():.2f}")
    print(f"   Score range: {df['score_avg'].min():.1f} - {df['score_avg'].max():.1f}")
    print(f"   Median score: {df['score_avg'].median():.2f}")
    
    print(f"\n🤝 Evaluator Agreement:")
    correlation = df['score_me'].corr(df['score_other'])
    print(f"   Correlation between evaluators: {correlation:.3f}")
    print(f"   Mean absolute difference: {df['score_diff'].mean():.2f}")
    
    print(f"\n🏆 Top 5 Performing Topics:")
    topic_performance = df.groupby('topic_name')['score_avg'].mean().sort_values(ascending=False)
    for i, (topic, score) in enumerate(topic_performance.head().items(), 1):
        print(f"   {i}. {topic}: {score:.2f}")
    
    print(f"\n📉 Bottom 5 Performing Topics:")
    for i, (topic, score) in enumerate(topic_performance.tail().items(), 1):
        print(f"   {i}. {topic}: {score:.2f}")
    
    print(f"\n📝 Text Analysis:")
    print(f"   Average answer length: {df['answer_length'].mean():.0f} characters")
    print(f"   Average word count: {df['word_count'].mean():.0f} words")
    
    print(f"\n🎯 Key Insights:")
    print(f"   • Questions cover {df['topic'].nunique()} different programming topics")
    print(f"   • Score correlation between evaluators: {correlation:.3f} ({'Strong' if correlation > 0.7 else 'Moderate' if correlation > 0.5 else 'Weak'} agreement)")
    print(f"   • Most challenging topic: {topic_performance.tail(1).index[0]} ({topic_performance.tail(1).iloc[0]:.2f})")
    print(f"   • Best performing topic: {topic_performance.head(1).index[0]} ({topic_performance.head(1).iloc[0]:.2f})")

def main():
    """Main function to run the analysis"""
    print("🚀 Loading and analyzing Mohler dataset...")
    
    # Load data
    df = load_and_clean_data('mohler_dataset_edited.csv')
    
    # Add derived columns
    df['score_diff'] = abs(df['score_me'] - df['score_other'])
    df['answer_length'] = df['student_answer'].str.len()
    df['word_count'] = df['student_answer'].str.split().str.len()
    
    # Create visualizations
    print("📊 Creating comprehensive analysis dashboard...")
    create_comprehensive_analysis(df)
    
    print("📈 Creating detailed topic analysis...")
    create_detailed_topic_analysis(df)
    
    # Print summary statistics
    print_summary_statistics(df)
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*80)
    print("Generated files:")
    print("   📄 mohler_analysis_dashboard.png")
    print("   📄 detailed_topic_analysis.png")
    print("\nThe visualizations provide insights into:")
    print("   • Score distributions and evaluator agreement")
    print("   • Topic-wise performance analysis")
    print("   • Question difficulty patterns")
    print("   • Text-based correlations with scores")
    print("   • Overall assessment effectiveness")

if __name__ == "__main__":
    main() 