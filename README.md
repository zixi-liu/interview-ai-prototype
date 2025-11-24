# Interview Feedback System

An AI-powered interview feedback system that analyzes interview transcriptions and provides hiring recommendations using LiteLLM.

## Features

- Analyzes interview transcriptions to generate hiring decisions (Strong Hire, Weak Hire, No Hire)
- Provides detailed checkpoints and reasoning for each decision
- Supports multiple LLM providers through LiteLLM (OpenAI, Anthropic, etc.)
- Customizable focus areas for evaluation
- Text-based output for easy integration

## Setup

### Prerequisites

- **Docker** (recommended) OR Python 3.8 or higher
- API key for at least one LLM provider (OpenAI, Anthropic, etc.)

### Option 1: Docker Installation (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd interview-ai-prototype
```

2. Set up your API keys:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
```bash
# For OpenAI
OPENAI_API_KEY=your_actual_api_key_here

# For Anthropic (Claude)
ANTHROPIC_API_KEY=your_actual_api_key_here
```

3. Build and run with Docker:
```bash
# Using the deployment script
./deploy.sh run

# OR using docker-compose
docker-compose up -d
```

### Option 2: Local Python Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd interview-ai-prototype
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
```bash
# For OpenAI
OPENAI_API_KEY=your_actual_api_key_here

# For Anthropic (Claude)
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Usage

### Docker Usage

```bash
# Build and run the container
./deploy.sh run

# Run the example scenarios
./deploy.sh example

# Access interactive shell in container
./deploy.sh interactive

# View container logs
./deploy.sh logs

# Stop the container
./deploy.sh stop

# Clean up (stop and remove container and image)
./deploy.sh clean
```

Using docker-compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Run example in the container
docker-compose exec interview-analyzer python example_usage.py

# Stop the service
docker-compose down
```

### Basic Python Usage

```python
from interview_analyzer import InterviewAnalyzer

# Initialize the analyzer
analyzer = InterviewAnalyzer(model="gpt-4o-mini")

# Analyze an interview
transcription = """
Interviewer: Can you explain recursion?
Candidate: Recursion is when a function calls itself...
"""

result = analyzer.analyze_interview(
    transcription=transcription,
    role="Software Engineer",
    level="Mid-level"
)

# Print formatted output
print(analyzer.format_output(result))
```

### Running the Examples

The repository includes several examples:

```bash
# Run the main example
python interview_analyzer.py

# Run all example scenarios
python example_usage.py
```

### Customizing the Analysis

You can customize the analysis with focus areas:

```python
result = analyzer.analyze_interview(
    transcription=transcription,
    role="Software Engineer",
    level="Senior",
    focus_areas=["System design", "Leadership", "Code quality"]
)
```

### Supported Models

LiteLLM supports 100+ models. Some common ones:

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- **Google**: `gemini-1.5-pro`, `gemini-1.5-flash`
- **Local**: `ollama/llama3`, `ollama/mistral`

See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for the full list.

To use a different model:

```python
analyzer = InterviewAnalyzer(model="claude-3-5-sonnet-20241022")
```

## Output Format

The system provides:

1. **Decision**: Strong Hire, Weak Hire, or No Hire
2. **Checkpoints**: 5-8 evaluation points with Pass/Fail/Partial ratings
3. **Reasoning**: Detailed explanation of the decision
4. **Raw Feedback**: Complete LLM response for further analysis

Example output:

```
============================================================
INTERVIEW FEEDBACK REPORT
============================================================

Model Used: gpt-4o-mini

HIRING DECISION:     Weak Hire

------------------------------------------------------------
CHECKPOINTS:
------------------------------------------------------------
1. Technical Knowledge: Partial - Demonstrates basic understanding but lacks depth
2. Problem Solving: Pass - Good analytical approach
3. Communication: Pass - Clear and articulate responses
...

------------------------------------------------------------
REASONING:
------------------------------------------------------------
The candidate shows promise in problem-solving abilities and communication
skills. However, there are gaps in technical depth that would need to be
addressed...
============================================================
```

## Project Structure

```
interview-ai-prototype/
├── interview_analyzer.py    # Main analyzer class
├── example_usage.py         # Example usage scenarios
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── deploy.sh              # Deployment script
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

## How It Works

1. **Input**: The system takes interview transcription text
2. **Processing**: Uses LiteLLM to send the transcription to an LLM with a structured prompt
3. **Analysis**: The LLM evaluates the candidate based on:
   - Technical skills
   - Problem-solving ability
   - Communication clarity
   - Experience level appropriateness
   - Custom focus areas (if provided)
4. **Output**: Returns a structured decision with checkpoints and reasoning

## Customization

### Modifying the Prompt

Edit the `_build_prompt` method in `interview_analyzer.py` to customize evaluation criteria:

```python
def _build_prompt(self, transcription, role, level, focus_areas):
    # Modify this method to change evaluation criteria
    prompt = f"""Your custom prompt here..."""
    return prompt
```

### Adding New Features

The `InterviewAnalyzer` class is designed to be extensible. You can:

- Add scoring systems
- Implement comparison between candidates
- Export to different formats (JSON, PDF, etc.)
- Integrate with applicant tracking systems

## Cost Considerations

Using LLM APIs incurs costs. Approximate costs per analysis:

- **gpt-4o-mini**: ~$0.01 per interview
- **gpt-4o**: ~$0.05 per interview
- **claude-3-5-haiku-20241022**: ~$0.01 per interview
- **claude-3-5-sonnet-20241022**: ~$0.03 per interview

Using local models with Ollama is free but requires local setup.

## Best Practices

1. **Clear Transcriptions**: Better transcriptions lead to better analysis
2. **Consistent Format**: Use the same role/level conventions
3. **Human Review**: AI feedback should augment, not replace, human judgment
4. **Bias Awareness**: Review outputs for potential biases
5. **Privacy**: Don't include PII in transcriptions if storing results

## Docker Deployment Details

### Deployment Script Commands

The `deploy.sh` script provides several commands:

- `build` - Build the Docker image only
- `run` - Build and run the container in detached mode
- `interactive` - Run container with interactive bash shell
- `example` - Run the example usage scenarios
- `stop` - Stop the running container
- `logs` - Show and follow container logs
- `clean` - Stop and remove container and image
- `help` - Show usage information

### Environment Variables

Set `VERSION` to tag your Docker image:

```bash
VERSION=v1.0 ./deploy.sh build
```

### Volume Mounts

The Docker setup mounts:
- `./data` - For input/output files
- `./transcriptions` - For interview transcription files (read-only)

Create these directories if needed:

```bash
mkdir -p data transcriptions
```

## Troubleshooting

### Docker Issues

If you encounter Docker problems:
- Ensure Docker daemon is running: `docker info`
- Check if port conflicts exist
- Verify `.env` file is in the project root
- Run `./deploy.sh clean` and try again

### API Key Issues

If you get authentication errors:
- Check that your `.env` file exists and has the correct API key
- Verify the API key is valid and has available credits
- Make sure you're using the right key for your chosen model
- In Docker, ensure the `.env` file is being mounted correctly

### Model Not Found

If you get "model not found" errors:
- Check the [LiteLLM providers list](https://docs.litellm.ai/docs/providers)
- Verify the model name is correct
- Ensure you have the right API key configured

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
