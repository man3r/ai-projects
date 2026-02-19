"""
Unit Test Writer Agent
Analyzes Python functions and generates comprehensive pytest tests.
"""

import anthropic
import os
import sys
from pathlib import Path
import json


class UnitTestAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = self._create_tools()
        
    def _create_tools(self):
        """Define tools the agent can use"""
        return [
            {
                "name": "read_source_file",
                "description": "Read a Python source file to analyze its functions. Returns the file content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python source file (e.g., 'src/calculator.py')"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "write_test_file",
                "description": "Write generated test code to a file in the tests directory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path where test file should be written (e.g., 'tests/test_calculator.py')"
                        },
                        "content": {
                            "type": "string",
                            "description": "The complete test code to write"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "list_functions",
                "description": "List all function definitions in a Python file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return its result"""
        try:
            if tool_name == "read_source_file":
                file_path = Path(tool_input["file_path"])
                if not file_path.exists():
                    return f"Error: File {file_path} does not exist"
                content = file_path.read_text()
                return f"File content of {file_path}:\n\n{content}"
            
            elif tool_name == "write_test_file":
                file_path = Path(tool_input["file_path"])
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(tool_input["content"])
                return f"✓ Successfully wrote test file to {file_path}"
            
            elif tool_name == "list_functions":
                file_path = Path(tool_input["file_path"])
                if not file_path.exists():
                    return f"Error: File {file_path} does not exist"
                
                content = file_path.read_text()
                # Simple function extraction (can be improved with AST)
                functions = []
                for line in content.split('\n'):
                    if line.strip().startswith('def '):
                        func_name = line.split('def ')[1].split('(')[0]
                        functions.append(func_name)
                
                return f"Functions found: {', '.join(functions)}"
            
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def run(self, task: str, max_iterations: int = 10) -> str:
        """
        Run the agent on a task, allowing it to use tools autonomously.
        
        Args:
            task: The task description (e.g., "Generate tests for src/calculator.py")
            max_iterations: Maximum number of tool use iterations
            
        Returns:
            Final response from the agent
        """
        print(f"\n🤖 Unit Test Agent Starting...")
        print(f"📋 Task: {task}\n")
        
        # Initial system message to guide the agent
        system_prompt = """You are an expert Python test engineer. Your job is to:

1. Read Python source files using the read_source_file tool
2. Analyze the functions and their logic
3. Generate comprehensive pytest unit tests that cover:
   - Happy path scenarios
   - Edge cases (empty inputs, None, zeros, negative numbers)
   - Error conditions with appropriate pytest.raises assertions
   - Boundary values
4. Write the tests to a file using write_test_file tool

Guidelines for test generation:
- Use descriptive test names (test_function_name_scenario)
- Include docstrings explaining what each test validates
- Use pytest fixtures if appropriate
- Add parametrize for testing multiple inputs efficiently
- Mock external dependencies if needed
- Follow PEP 8 style guidelines

Always use the tools to read files and write tests. Don't make assumptions about file content."""

        messages = [{"role": "user", "content": task}]
        
        for iteration in range(max_iterations):
            print(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Call Claude with tools
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tools,
                messages=messages
            )
            
            print(f"⚡ Stop reason: {response.stop_reason}")
            
            # Check if we're done
            if response.stop_reason == "end_turn":
                # Extract text responses
                final_response = []
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_response.append(block.text)
                
                result = "\n".join(final_response)
                print(f"\n✅ Agent completed task!\n")
                return result
            
            # Add assistant's response to conversation
            messages.append({"role": "assistant", "content": response.content})
            
            # Process any tool uses
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"🔧 Using tool: {tool_name}")
                    print(f"   Input: {json.dumps(tool_input, indent=2)}")
                    
                    # Execute the tool
                    result = self._execute_tool(tool_name, tool_input)
                    print(f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results to conversation
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
            else:
                # No tools used but not end_turn - shouldn't happen
                break
        
        return "⚠️ Maximum iterations reached without completion"


def main():
    """Example usage of the Unit Test Agent"""
    
    # Get file path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python ut_writer_agent.py <source_file_path>")
        print("Example: python ut_writer_agent.py src/calculator.py")
        sys.exit(1)
    
    source_file = sys.argv[1]
    test_file = f"tests/test_{Path(source_file).stem}.py"
    
    print("=" * 60)
    print("Unit Test Agent Demo")
    print("=" * 60)
    
    # Initialize and run agent
    agent = UnitTestAgent()
    result = agent.run(
        f"Read the file '{source_file}' and generate comprehensive unit tests. "
        f"Write the tests to '{test_file}'."
    )
    
    print("\n" + "=" * 60)
    print("Final Result:")
    print("=" * 60)
    print(result)
    
    # Check if test file was created
    test_file_path = Path(test_file)
    if test_file_path.exists():
        print(f"\n✅ Test file created: {test_file_path}")
        print("\nYou can now run the tests with:")
        print(f"  pytest {test_file} -v")


if __name__ == "__main__":
    main()
