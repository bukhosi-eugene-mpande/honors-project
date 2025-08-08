#!/usr/bin/env python3
"""
Pipeline Visualization
=====================

This script creates comprehensive visualizations for the rubric assessment pipeline.
"""

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import json
from datetime import datetime
import seaborn as sns

class PipelineVisualizer:
    """Class for visualizing the rubric assessment pipeline"""
    
    def __init__(self):
        self.colors = {
            'initialize': '#FF6B6B',
            'load_rubrics': '#4ECDC4',
            'generate_answers': '#45B7D1',
            'nlp_assessment': '#96CEB4',
            'score_calculation': '#FFEAA7',
            'results_analysis': '#DDA0DD',
            'generate_report': '#98D8C8'
        }
        
    def create_pipeline_architecture(self):
        """Create the main pipeline architecture visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Left: Step Functions workflow
        self._create_step_functions_workflow(ax1)
        
        # Right: Data flow diagram
        self._create_data_flow_diagram(ax2)
        
        plt.suptitle('Rubric Assessment Pipeline Architecture', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('pipeline_architecture.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _create_step_functions_workflow(self, ax):
        """Create Step Functions workflow visualization"""
        G = nx.DiGraph()
        
        # Define nodes and their positions
        nodes = [
            ('Initialize\nPipeline', (0, 6)),
            ('Load\nRubrics', (2, 6)),
            ('Generate Answer\nVariations', (4, 6)),
            ('NLP\nAssessment', (6, 6)),
            ('Score\nCalculation', (8, 6)),
            ('Results\nAnalysis', (10, 6)),
            ('Generate\nReport', (12, 6))
        ]
        
        # Add nodes
        for node, pos in nodes:
            G.add_node(node, pos=pos)
        
        # Add edges
        edges = [
            ('Initialize\nPipeline', 'Load\nRubrics'),
            ('Load\nRubrics', 'Generate Answer\nVariations'),
            ('Generate Answer\nVariations', 'NLP\nAssessment'),
            ('NLP\nAssessment', 'Score\nCalculation'),
            ('Score\nCalculation', 'Results\nAnalysis'),
            ('Results\nAnalysis', 'Generate\nReport')
        ]
        
        for edge in edges:
            G.add_edge(edge[0], edge[1])
        
        # Draw the graph
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw nodes with different colors
        node_colors = [self.colors.get(node.split('\n')[0].lower().replace(' ', '_'), '#CCCCCC') 
                      for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
        
        ax.set_title('AWS Step Functions Workflow', fontweight='bold')
        ax.axis('off')
    
    def _create_data_flow_diagram(self, ax):
        """Create data flow diagram"""
        # Define data stores and processes
        data_stores = {
            'S3 Bucket': (2, 8),
            'DynamoDB': (2, 4),
            'Lambda Functions': (6, 6),
            'AWS Comprehend': (10, 6),
            'Results Storage': (14, 6)
        }
        
        processes = {
            'Rubric\nGeneration': (4, 8),
            'Answer\nGeneration': (4, 4),
            'NLP\nProcessing': (8, 8),
            'Score\nAggregation': (8, 4),
            'Report\nGeneration': (12, 6)
        }
        
        # Draw data stores (rectangles)
        for store, pos in data_stores.items():
            rect = plt.Rectangle((pos[0]-0.5, pos[1]-0.3), 1, 0.6, 
                               facecolor='lightblue', edgecolor='black', alpha=0.7)
            ax.add_patch(rect)
            ax.text(pos[0], pos[1], store, ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Draw processes (circles)
        for process, pos in processes.items():
            circle = plt.Circle(pos, 0.4, facecolor='lightgreen', edgecolor='black', alpha=0.7)
            ax.add_patch(circle)
            ax.text(pos[0], pos[1], process, ha='center', va='center', fontsize=7, fontweight='bold')
        
        # Draw data flow arrows
        arrows = [
            ((2, 8), (4, 8)),  # S3 to Rubric Generation
            ((4, 8), (4, 4)),  # Rubric to Answer Generation
            ((4, 4), (8, 8)),  # Answers to NLP Processing
            ((8, 8), (8, 4)),  # NLP to Score Aggregation
            ((8, 4), (12, 6)), # Scores to Report Generation
            ((12, 6), (14, 6)) # Report to Results Storage
        ]
        
        for start, end in arrows:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        
        ax.set_xlim(0, 16)
        ax.set_ylim(2, 10)
        ax.set_title('Data Flow Architecture', fontweight='bold')
        ax.axis('off')
    
    def create_rubric_visualization(self, rubrics_data):
        """Create visualization of rubric structure"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Rubric Structure Analysis', fontsize=16, fontweight='bold')
        
        # 1. Rubric criteria distribution
        ax1 = axes[0, 0]
        topics = list(rubrics_data.keys())
        criteria_counts = [len(rubric['criteria']) for rubric in rubrics_data.values()]
        
        bars = ax1.bar(topics, criteria_counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Number of Criteria per Topic')
        ax1.set_ylabel('Number of Criteria')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, criteria_counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        # 2. Points distribution
        ax2 = axes[0, 1]
        max_scores = [rubric['max_score'] for rubric in rubrics_data.values()]
        
        bars = ax2.bar(topics, max_scores, color=['#96CEB4', '#FFEAA7', '#DDA0DD'])
        ax2.set_title('Maximum Points per Topic')
        ax2.set_ylabel('Maximum Points')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, score in zip(bars, max_scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(score), ha='center', va='bottom')
        
        # 3. Criteria breakdown
        ax3 = axes[1, 0]
        all_criteria = []
        for topic, rubric in rubrics_data.items():
            for criterion in rubric['criteria']:
                all_criteria.append({
                    'topic': topic,
                    'criterion': criterion['criterion'],
                    'points': criterion['points']
                })
        
        df_criteria = pd.DataFrame(all_criteria)
        
        # Create a heatmap of criteria points
        pivot_table = df_criteria.pivot_table(index='topic', columns='criterion', 
                                            values='points', fill_value=0)
        
        sns.heatmap(pivot_table, annot=True, cmap='YlOrRd', ax=ax3)
        ax3.set_title('Criteria Points Distribution')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Keyword analysis
        ax4 = axes[1, 1]
        all_keywords = []
        for topic, rubric in rubrics_data.items():
            for criterion in rubric['criteria']:
                for keyword in criterion['keywords']:
                    all_keywords.append({
                        'topic': topic,
                        'keyword': keyword,
                        'criterion': criterion['criterion']
                    })
        
        df_keywords = pd.DataFrame(all_keywords)
        keyword_counts = df_keywords['keyword'].value_counts().head(10)
        
        bars = ax4.barh(range(len(keyword_counts)), keyword_counts.values, color='lightcoral')
        ax4.set_yticks(range(len(keyword_counts)))
        ax4.set_yticklabels(keyword_counts.index, fontsize=8)
        ax4.set_title('Top 10 Most Common Keywords')
        ax4.set_xlabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('rubric_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_nlp_analysis_visualization(self, nlp_results):
        """Create visualization of NLP analysis results"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('NLP Analysis Results', fontsize=16, fontweight='bold')
        
        # Collect all NLP data
        all_sentiments = []
        all_complexities = []
        all_scores = []
        all_key_phrases = []
        
        for topic_key, topic_results in nlp_results.items():
            for question, variations in topic_results.items():
                for variation in variations:
                    nlp_analysis = variation['nlp_analysis']
                    all_sentiments.append(nlp_analysis['sentiment']['sentiment'])
                    all_complexities.append(nlp_analysis['complexity']['complexity_level'])
                    all_scores.append(variation['final_score'])
                    all_key_phrases.extend(nlp_analysis['key_phrases'])
        
        # 1. Sentiment distribution
        ax1 = axes[0, 0]
        sentiment_counts = pd.Series(all_sentiments).value_counts()
        ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
        ax1.set_title('Sentiment Distribution')
        
        # 2. Complexity distribution
        ax2 = axes[0, 1]
        complexity_counts = pd.Series(all_complexities).value_counts()
        bars = ax2.bar(range(len(complexity_counts)), complexity_counts.values, color='lightblue')
        ax2.set_xticks(range(len(complexity_counts)))
        ax2.set_xticklabels(complexity_counts.index, rotation=45, ha='right')
        ax2.set_title('Text Complexity Distribution')
        ax2.set_ylabel('Count')
        
        # 3. Score distribution
        ax3 = axes[0, 2]
        ax3.hist(all_scores, bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        ax3.set_title('Score Distribution')
        ax3.set_xlabel('Score')
        ax3.set_ylabel('Frequency')
        ax3.axvline(np.mean(all_scores), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(all_scores):.2f}')
        ax3.legend()
        
        # 4. Sentiment vs Score
        ax4 = axes[1, 0]
        sentiment_score_data = pd.DataFrame({
            'sentiment': all_sentiments,
            'score': all_scores
        })
        
        sentiment_avg = sentiment_score_data.groupby('sentiment')['score'].mean()
        bars = ax4.bar(range(len(sentiment_avg)), sentiment_avg.values, color='orange')
        ax4.set_xticks(range(len(sentiment_avg)))
        ax4.set_xticklabels(sentiment_avg.index)
        ax4.set_title('Average Score by Sentiment')
        ax4.set_ylabel('Average Score')
        
        # 5. Complexity vs Score
        ax5 = axes[1, 1]
        complexity_score_data = pd.DataFrame({
            'complexity': all_complexities,
            'score': all_scores
        })
        
        complexity_avg = complexity_score_data.groupby('complexity')['score'].mean()
        bars = ax5.bar(range(len(complexity_avg)), complexity_avg.values, color='purple')
        ax5.set_xticks(range(len(complexity_avg)))
        ax5.set_xticklabels(complexity_avg.index, rotation=45, ha='right')
        ax5.set_title('Average Score by Complexity')
        ax5.set_ylabel('Average Score')
        
        # 6. Top key phrases
        ax6 = axes[1, 2]
        phrase_counts = pd.Series(all_key_phrases).value_counts().head(10)
        bars = ax6.barh(range(len(phrase_counts)), phrase_counts.values, color='lightcoral')
        ax6.set_yticks(range(len(phrase_counts)))
        ax6.set_yticklabels(phrase_counts.index, fontsize=8)
        ax6.set_title('Top 10 Key Phrases')
        ax6.set_xlabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('nlp_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_performance_dashboard(self, score_analysis, overall_stats):
        """Create comprehensive performance dashboard"""
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Overall performance summary
        ax1 = fig.add_subplot(gs[0, :2])
        summary_data = {
            'Total Answers': overall_stats['total_answers'],
            'Average Score': f"{overall_stats['avg_score']:.2f}",
            'Topics Covered': len(score_analysis),
            'Processing Complete': 'Yes'
        }
        
        y_pos = range(len(summary_data))
        ax1.barh(y_pos, [1] * len(summary_data), color='lightblue', alpha=0.7)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(summary_data.keys())
        ax1.set_xlim(0, 1)
        ax1.set_title('Pipeline Performance Summary', fontweight='bold')
        
        # Add values as text
        for i, (key, value) in enumerate(summary_data.items()):
            ax1.text(0.5, i, str(value), ha='center', va='center', fontweight='bold')
        
        # 2. Topic performance comparison
        ax2 = fig.add_subplot(gs[0, 2:])
        topics = list(score_analysis.keys())
        avg_scores = [score_analysis[topic]['avg_score'] for topic in topics]
        
        bars = ax2.barh(range(len(topics)), avg_scores, color='lightgreen')
        ax2.set_yticks(range(len(topics)))
        ax2.set_yticklabels(topics, fontsize=9)
        ax2.set_title('Average Score by Topic', fontweight='bold')
        ax2.set_xlabel('Average Score')
        
        # Add score labels
        for bar, score in zip(bars, avg_scores):
            ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{score:.2f}', ha='left', va='center', fontsize=8)
        
        # 3. Score distribution
        ax3 = fig.add_subplot(gs[1, :2])
        all_scores = []
        for topic_data in score_analysis.values():
            for question_data in topic_data['questions'].values():
                all_scores.extend(question_data['scores'])
        
        ax3.hist(all_scores, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.set_title('Overall Score Distribution', fontweight='bold')
        ax3.set_xlabel('Score')
        ax3.set_ylabel('Frequency')
        ax3.axvline(np.mean(all_scores), color='red', linestyle='--',
                   label=f'Mean: {np.mean(all_scores):.2f}')
        ax3.legend()
        
        # 4. Answer type performance
        ax4 = fig.add_subplot(gs[1, 2:])
        answer_type_perf = overall_stats['answer_type_performance']
        if answer_type_perf:
            types = list(answer_type_perf.keys())
            scores = list(answer_type_perf.values())
            
            bars = ax4.bar(range(len(types)), scores, color='orange', alpha=0.7)
            ax4.set_xticks(range(len(types)))
            ax4.set_xticklabels(types, rotation=45, ha='right', fontsize=8)
            ax4.set_title('Performance by Answer Type', fontweight='bold')
            ax4.set_ylabel('Average Score')
        
        # 5. NLP metrics summary
        ax5 = fig.add_subplot(gs[2, :])
        nlp_metrics = overall_stats['nlp_metrics']
        
        # Sentiment distribution
        sentiment_data = nlp_metrics['sentiment_distribution']
        if sentiment_data:
            sentiment_labels = list(sentiment_data.keys())
            sentiment_counts = list(sentiment_data.values())
            
            bars = ax5.bar(range(len(sentiment_labels)), sentiment_counts, color='lightcoral')
            ax5.set_xticks(range(len(sentiment_labels)))
            ax5.set_xticklabels(sentiment_labels)
            ax5.set_title('NLP Metrics Summary', fontweight='bold')
            ax5.set_ylabel('Count')
        
        # 6. Complexity distribution
        ax6 = fig.add_subplot(gs[3, :])
        complexity_data = nlp_metrics['complexity_distribution']
        if complexity_data:
            complexity_labels = list(complexity_data.keys())
            complexity_counts = list(complexity_data.values())
            
            bars = ax6.bar(range(len(complexity_labels)), complexity_counts, color='lightblue')
            ax6.set_xticks(range(len(complexity_labels)))
            ax6.set_xticklabels(complexity_labels, rotation=45, ha='right')
            ax6.set_title('Text Complexity Distribution', fontweight='bold')
            ax6.set_ylabel('Count')
        
        plt.suptitle('Rubric Assessment Pipeline Performance Dashboard', fontsize=16, fontweight='bold')
        plt.savefig('performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main function to demonstrate pipeline visualization"""
    visualizer = PipelineVisualizer()
    
    # Create pipeline architecture
    print("Creating pipeline architecture visualization...")
    visualizer.create_pipeline_architecture()
    
    # Sample data for demonstration
    sample_rubrics = {
        "classes_objects": {
            "topic": "Classes & Objects",
            "criteria": [
                {"criterion": "Class Definition", "points": 2, "keywords": ["class", "data members"]},
                {"criterion": "Constructor Knowledge", "points": 2, "keywords": ["constructor", "initialization"]},
                {"criterion": "Access Specifiers", "points": 1, "keywords": ["public", "private"]}
            ],
            "max_score": 5
        },
        "pointers_memory": {
            "topic": "Pointers & Memory",
            "criteria": [
                {"criterion": "Pointer Declaration", "points": 2, "keywords": ["pointer", "address"]},
                {"criterion": "Dereferencing", "points": 2, "keywords": ["dereference", "*"]},
                {"criterion": "Memory Management", "points": 1, "keywords": ["malloc", "free"]}
            ],
            "max_score": 5
        },
        "functions_scope": {
            "topic": "Functions & Scope",
            "criteria": [
                {"criterion": "Function Definition", "points": 2, "keywords": ["function", "parameters"]},
                {"criterion": "Variable Scope", "points": 2, "keywords": ["scope", "local", "global"]},
                {"criterion": "Function Overloading", "points": 1, "keywords": ["overloading", "same name"]}
            ],
            "max_score": 5
        }
    }
    
    # Create rubric visualization
    print("Creating rubric analysis visualization...")
    visualizer.create_rubric_visualization(sample_rubrics)
    
    print("Pipeline visualization complete!")
    print("Generated files:")
    print("- pipeline_architecture.png")
    print("- rubric_analysis.png")

if __name__ == "__main__":
    main() 