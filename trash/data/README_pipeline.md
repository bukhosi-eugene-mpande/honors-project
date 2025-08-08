# Rubric Assessment Pipeline

## Overview

This project implements a comprehensive automated assessment pipeline using AWS Step Functions, Lambda functions, and NLP techniques. The pipeline generates multiple answer variations based on rubrics and assesses them using advanced NLP analysis.

## Architecture

### Pipeline Components

1. **AWS Step Functions** - Orchestrates the entire workflow
2. **Lambda Functions** - Individual processing steps
3. **AWS Comprehend** - NLP analysis and sentiment detection
4. **S3** - Data storage and pipeline artifacts
5. **DynamoDB** - Metadata and results storage

### Pipeline Flow

```
Initialize Pipeline → Load Rubrics → Generate Answer Variations → 
NLP Assessment → Score Calculation → Results Analysis → Generate Report
```

## Features

### 🎯 **Rubric-Based Assessment**
- Dynamic rubric creation for different topics
- Multi-criteria scoring system
- Keyword-based content analysis
- Configurable point allocation

### 🤖 **NLP-Powered Analysis**
- Sentiment analysis using AWS Comprehend
- Text complexity assessment
- Key phrase extraction
- Semantic similarity analysis
- Fallback analysis for offline processing

### 📊 **Comprehensive Scoring**
- Multi-factor scoring algorithm
- Rubric criteria weighting
- NLP metrics integration
- Performance analytics

### 📈 **Advanced Visualizations**
- Pipeline architecture diagrams
- Rubric structure analysis
- NLP results visualization
- Performance dashboards

## Files Structure

```
data/
├── rubric_assessment_pipeline.py      # Main pipeline class
├── pipeline_visualization.py          # Visualization tools
├── lambda_functions/
│   ├── initialize_pipeline.py         # Pipeline initialization
│   ├── load_rubrics.py               # Rubric loading
│   ├── generate_answers.py           # Answer generation
│   ├── nlp_assessment.py             # NLP analysis
│   └── calculate_scores.py           # Score calculation
├── README_pipeline.md                # This file
└── requirements_pipeline.txt         # Dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_pipeline.txt
```

### 2. Run Pipeline Demo

```bash
python rubric_assessment_pipeline.py
```

### 3. Generate Visualizations

```bash
python pipeline_visualization.py
```

## Detailed Usage

### Pipeline Initialization

```python
from rubric_assessment_pipeline import RubricAssessmentPipeline

# Initialize pipeline
pipeline = RubricAssessmentPipeline()

# Generate sample rubrics
rubrics = pipeline.generate_sample_rubrics()

# Create Step Functions definition
step_functions_def = pipeline.create_step_functions_definition()

# Visualize pipeline
pipeline.visualize_pipeline()
```

### Rubric Creation

```python
# Create a custom rubric
rubric = pipeline.create_rubric_template(
    "Data Structures",
    [
        {
            "criterion": "Understanding",
            "description": "Student demonstrates understanding",
            "points": 3,
            "keywords": ["data", "structure", "algorithm"]
        },
        {
            "criterion": "Implementation",
            "description": "Student can implement concepts",
            "points": 2,
            "keywords": ["code", "implementation", "programming"]
        }
    ]
)
```

### Answer Generation

```python
# Generate answer variations
question = "What is a linked list?"
variations = pipeline.generate_answer_variations(question, rubric)

# Variations include:
# - Perfect answer (all criteria met)
# - Partial answers (some criteria met)
# - Weak answer (minimal understanding)
# - Incorrect answer (wrong concepts)
```

### NLP Assessment

```python
# Assess an answer using NLP
assessment = pipeline.assess_answer_with_nlp(answer, rubric)

# Assessment includes:
# - Keyword matching
# - Sentiment analysis
# - Text complexity
# - Semantic similarity
# - Combined scoring
```

## AWS Deployment

### Prerequisites

1. AWS CLI configured
2. Appropriate IAM permissions
3. S3 bucket for data storage
4. DynamoDB table for metadata

### Step Functions Setup

1. **Create State Machine**

```bash
aws stepfunctions create-state-machine \
    --name "RubricAssessmentPipeline" \
    --definition file://step_functions_definition.json \
    --role-arn "arn:aws:iam::YOUR_ACCOUNT:role/StepFunctionsExecutionRole"
```

2. **Deploy Lambda Functions**

```bash
# Package and deploy each Lambda function
cd lambda_functions
zip -r initialize_pipeline.zip initialize_pipeline.py
aws lambda create-function \
    --function-name initialize-pipeline \
    --runtime python3.9 \
    --handler initialize_pipeline.lambda_handler \
    --zip-file fileb://initialize_pipeline.zip \
    --role arn:aws:iam::YOUR_ACCOUNT:role/LambdaExecutionRole
```

### Environment Variables

Set the following environment variables for Lambda functions:

```bash
ASSESSMENT_BUCKET=your-assessment-bucket
ASSESSMENT_TABLE=rubric-assessments
RUBRIC_TABLE=rubrics
```

## Pipeline Steps

### 1. Initialize Pipeline
- Creates pipeline metadata
- Sets up S3 folder structure
- Initializes DynamoDB records

### 2. Load Rubrics
- Retrieves rubric definitions
- Validates rubric structure
- Stores rubrics for processing

### 3. Generate Answer Variations
- Creates perfect answers (all criteria met)
- Generates partial answers (some criteria met)
- Produces weak answers (minimal understanding)
- Creates incorrect answers (wrong concepts)

### 4. NLP Assessment
- Performs sentiment analysis
- Extracts key phrases
- Analyzes text complexity
- Calculates semantic similarity
- Combines NLP metrics with rubric scoring

### 5. Score Calculation
- Aggregates scores across criteria
- Calculates topic-level statistics
- Generates performance metrics
- Creates detailed analysis reports

### 6. Results Analysis
- Analyzes scoring patterns
- Identifies assessment effectiveness
- Generates insights and recommendations

### 7. Generate Report
- Creates comprehensive assessment reports
- Generates visualizations
- Exports results to various formats

## NLP Analysis Features

### Sentiment Analysis
- Positive/Negative/Neutral classification
- Confidence scoring
- Sentiment impact on final scores

### Text Complexity
- Flesch Reading Ease calculation
- Lexical diversity analysis
- Sentence structure assessment
- Vocabulary complexity metrics

### Key Phrase Extraction
- Important concept identification
- Technical term recognition
- Phrase frequency analysis

### Semantic Similarity
- Concept overlap calculation
- Expected vs actual content matching
- Topic relevance scoring

## Scoring Algorithm

The final score combines multiple factors:

```
Final Score = (Rubric Score × 0.6) + 
              (Sentiment Score × 0.2) + 
              (Complexity Score × 0.1) + 
              (Key Phrases Score × 0.1)
```

### Rubric Scoring (60%)
- Keyword matching
- Criteria fulfillment
- Point allocation

### Sentiment Scoring (20%)
- Positive sentiment boosts scores
- Negative sentiment reduces scores
- Neutral sentiment has minimal impact

### Complexity Scoring (10%)
- Appropriate complexity is rewarded
- Overly simple or complex text is penalized
- Balanced complexity gets optimal scores

### Key Phrases Scoring (10%)
- More relevant key phrases increase scores
- Technical term usage is rewarded
- Concept coverage is assessed

## Visualization Features

### Pipeline Architecture
- Step Functions workflow diagram
- Data flow visualization
- Component interaction mapping

### Rubric Analysis
- Criteria distribution charts
- Points allocation visualization
- Keyword frequency analysis
- Topic coverage mapping

### NLP Results
- Sentiment distribution
- Complexity analysis
- Key phrase frequency
- Score correlation analysis

### Performance Dashboard
- Overall performance metrics
- Topic-wise comparison
- Answer type analysis
- NLP metrics summary

## Monitoring and Analytics

### Pipeline Metrics
- Execution time tracking
- Success/failure rates
- Resource utilization
- Cost analysis

### Assessment Quality
- Scoring consistency
- Evaluator agreement
- Rubric effectiveness
- NLP accuracy

### Performance Insights
- Topic difficulty analysis
- Student performance patterns
- Assessment reliability
- Improvement recommendations

## Error Handling

### Fallback Mechanisms
- Offline NLP analysis when AWS Comprehend is unavailable
- Graceful degradation of features
- Error logging and reporting

### Data Validation
- Input validation for all pipeline steps
- Rubric structure verification
- Answer format checking
- Score range validation

## Security Considerations

### Data Protection
- Encryption at rest and in transit
- IAM role-based access control
- S3 bucket policies
- DynamoDB access controls

### Privacy Compliance
- Student data anonymization
- Assessment result protection
- Audit trail maintenance
- GDPR compliance measures

## Cost Optimization

### Resource Management
- Lambda function optimization
- S3 lifecycle policies
- DynamoDB capacity planning
- Step Functions execution optimization

### Monitoring
- Cost tracking and alerts
- Resource utilization monitoring
- Performance optimization
- Scaling recommendations

## Future Enhancements

### Planned Features
- Machine learning model integration
- Real-time assessment capabilities
- Multi-language support
- Advanced analytics dashboard

### Scalability Improvements
- Horizontal scaling support
- Multi-region deployment
- Performance optimization
- Enhanced monitoring

## Support and Documentation

### Troubleshooting
- Common error solutions
- Debugging guidelines
- Performance tuning tips
- Best practices

### API Documentation
- Lambda function APIs
- Step Functions integration
- S3 data formats
- DynamoDB schemas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions and support:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Note**: This pipeline is designed for educational assessment purposes and should be used in compliance with relevant privacy and data protection regulations. 