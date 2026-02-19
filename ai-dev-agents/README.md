# AI Development Agents

A multi-agent system for automating software development tasks like unit test generation, testing, and spec writing.

## Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install anthropic pytest
```

### 2. Set API Key

Get your API key from https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### 3. Run Your First Agent

```bash
python agents/ut_writer_agent.py
```

This will:
- Read `src/calculator.py`
- Generate comprehensive unit tests
- Write them to `tests/test_calculator.py`
- Show you the complete agent workflow with tool usage

### 4. Run the Generated Tests

```bash
pytest tests/test_calculator.py -v
```

## Project Structure

```
ai-dev-agents/
├── agents/
│   ├── __init__.py
│   └── ut_writer_agent.py     # Unit test writer agent
├── src/
│   └── calculator.py           # Example code to test
├── tests/
│   └── test_calculator.py      # Generated tests (created by agent)
└── README.md
```

## How the Agent Works

The Unit Test Agent uses Claude's function calling to:

1. **Read source files** - Uses `read_source_file` tool to get code
2. **Analyze functions** - Understands logic, inputs, outputs, error cases
3. **Generate tests** - Creates pytest tests covering all scenarios
4. **Write test files** - Uses `write_test_file` tool to save tests

### Agent Loop

```
User Task → Agent Plans → Uses Tools → Analyzes Results → Uses More Tools → Completes Task
```

The agent runs autonomously, deciding which tools to use and when.

## Next Steps

### Experiment with the Agent

Try modifying the task in `ut_writer_agent.py`:

```python
agent.run(
    "Read src/calculator.py and generate tests only for the divide and "
    "calculate_discount functions. Use parametrize for multiple test cases."
)
```

### Create Your Own Code to Test

1. Add a new file in `src/` with your own functions
2. Run the agent on it:

```python
agent = UnitTestAgent()
agent.run("Generate tests for src/your_module.py")
```

### Add More Agents

This is Week 1. Next you'll build:
- **Testing Agent** - Runs tests and analyzes failures
- **Spec Writer Agent** - Generates technical documentation
- **Coordinator** - Orchestrates multiple agents

## Understanding the Code

### Key Components

**Tools Definition** (`_create_tools`):
- Defines what the agent can do
- Each tool has a name, description, and input schema
- Claude decides when to use each tool

**Tool Execution** (`_execute_tool`):
- Implements the actual tool functionality
- Returns results to Claude
- Handles errors gracefully

**Agent Loop** (`run`):
- Sends task to Claude with available tools
- Processes tool use requests
- Feeds results back to Claude
- Continues until task complete

### Customization Ideas

1. **Add more tools**:
   - `run_linter` - Check code quality
   - `analyze_complexity` - Measure function complexity
   - `extract_docstring` - Get documentation

2. **Improve test generation**:
   - Add type hint analysis with `ast` module
   - Include coverage requirements
   - Generate fixtures automatically

3. **Add memory**:
   - Store common test patterns
   - Learn from previous test generations
   - Maintain project-specific conventions

## Troubleshooting

**"ANTHROPIC_API_KEY environment variable not set"**
- Make sure you exported the API key
- Try: `echo $ANTHROPIC_API_KEY` to verify

**Agent keeps running without finishing**
- Check the iteration logs
- The agent might be stuck in a tool loop
- Adjust `max_iterations` parameter

**Tests fail to run**
- Ensure pytest is installed: `pip install pytest`
- Check test file syntax
- The agent might have generated invalid Python

## Resources

- [Anthropic API Docs](https://docs.anthropic.com/)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

## Learning Goals (Week 1)

- ✅ Understand agent architecture
- ✅ Implement tool use
- ✅ Create autonomous agent loops
- ✅ Handle multi-step reasoning
- ⬜ Add error handling and retries
- ⬜ Implement evaluation metrics

Next week: Build the Testing Agent and create multi-agent coordination!
