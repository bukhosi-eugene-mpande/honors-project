# Mohler Dataset Visualization

This directory contains scripts to visualize and analyze the Mohler educational assessment dataset.

## Dataset Overview

The Mohler dataset contains student assessment data for a computer science/programming course with the following structure:

- **id**: Question identifier (e.g., 1.1, 1.2, etc.)
- **question**: The actual question text
- **desired_answer**: The expected/correct answer
- **student_answer**: The student's actual response
- **score_me**: Score given by one evaluator
- **score_other**: Score given by another evaluator
- **score_avg**: Average of the two scores

## Files

### Scripts
- `visualize_mohler_simple.py` - **Recommended**: Simplified visualization script with basic dependencies
- `visualize_mohler_dataset.py` - Full-featured script with additional analysis (requires wordcloud)

### Requirements
- `requirements_simple.txt` - Dependencies for the simplified script
- `requirements.txt` - Dependencies for the full-featured script

## Quick Start

### Option 1: Simple Visualization (Recommended)

1. Install dependencies:
```bash
pip install -r requirements_simple.txt
```

2. Run the visualization:
```bash
python visualize_mohler_simple.py
```

### Option 2: Full-Featured Visualization

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the visualization:
```bash
python visualize_mohler_dataset.py
```

## Generated Visualizations

The scripts will generate the following visualizations:

### Simple Script Output:
- `mohler_analysis_dashboard.png` - Comprehensive dashboard with 6 key visualizations
- `detailed_topic_analysis.png` - Detailed topic-wise analysis

### Full Script Output:
- `score_distribution_analysis.png` - Score distributions and evaluator agreement
- `topic_analysis.png` - Topic-specific performance analysis
- `question_difficulty_analysis.png` - Question difficulty patterns
- `text_analysis.png` - Text-based correlations with scores

## Key Insights Provided

### 1. Score Analysis
- Distribution of average scores across all questions
- Agreement between evaluators
- Score differences and variability

### 2. Topic Performance
- Average scores by programming topic
- Topic-wise difficulty analysis
- Performance ranking of different concepts

### 3. Question Difficulty
- Identification of easiest and hardest questions
- Score patterns across question order
- Correlation between question characteristics and scores

### 4. Text Analysis
- Relationship between answer length and scores
- Word count analysis
- Text-based performance patterns

### 5. Educational Insights
- Which programming concepts students struggle with most
- Evaluator consistency and reliability
- Assessment effectiveness and question quality

## Topic Categories

The dataset covers 12 main programming topics:

1. **Problem Solving & Life Cycle** - Software development process
2. **Classes & Objects** - Object-oriented programming basics
3. **Functions & Scope** - Function definitions and variable scope
4. **Arrays & Strings** - Array manipulation and string handling
5. **Sorting Algorithms** - Algorithm implementation and analysis
6. **Pointers & Memory** - Memory management and pointer operations
7. **Linked Lists** - Dynamic data structures
8. **Stacks** - Stack data structure and operations
9. **Queues** - Queue data structure and operations
10. **Trees** - Tree data structures and traversal
11. **Object-Oriented Programming** - Advanced OOP concepts
12. **Data Structures & Algorithms** - General algorithm analysis

## Usage Examples

### Basic Analysis
```python
import pandas as pd
from visualize_mohler_simple import load_and_clean_data

# Load the dataset
df = load_and_clean_data('mohler_dataset_edited.csv')

# Quick statistics
print(f"Average score: {df['score_avg'].mean():.2f}")
print(f"Total questions: {len(df)}")
```

### Custom Analysis
```python
# Find hardest questions
hardest_questions = df.nsmallest(5, 'score_avg')[['id', 'question', 'score_avg']]
print("Hardest questions:")
print(hardest_questions)

# Topic performance
topic_performance = df.groupby('topic_name')['score_avg'].mean().sort_values(ascending=False)
print("\nTopic performance:")
print(topic_performance)
```

## Troubleshooting

### Common Issues

1. **Import Error for wordcloud**: Use the simple script instead
2. **Matplotlib backend issues**: Try adding `plt.switch_backend('Agg')` at the top of the script
3. **Font issues**: The scripts use default fonts that should work on most systems

### System Requirements
- Python 3.7+
- 4GB+ RAM (for large datasets)
- Display capability for interactive plots (optional)

## Educational Applications

This visualization can be used for:

- **Curriculum Development**: Identify which topics need more emphasis
- **Assessment Design**: Improve question quality and difficulty balance
- **Student Support**: Target interventions for challenging concepts
- **Research**: Analyze educational effectiveness and learning patterns
- **Quality Assurance**: Evaluate evaluator consistency and reliability

## Data Privacy

The dataset contains educational assessment data. Ensure compliance with relevant privacy regulations when using this data for research or educational purposes. 