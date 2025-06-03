#!/usr/bin/env python3
"""
Example script demonstrating how to use the --url parameter 
to evaluate with external API services.

This script shows different usage patterns for the new --url functionality.
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and print its description"""
    print(f"\n{'='*60}")
    print(f"Example: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    # Note: In a real scenario, you would uncomment the line below to actually run the command
    # subprocess.run(cmd, check=True)
    print("(Command execution skipped in this example script)")

def main():
    """Demonstrate various usage patterns for the --url parameter"""
    
    print("Math Evaluation Harness - API Usage Examples")
    print("=" * 60)
    
    # Example 1: Basic usage with local vLLM server
    run_command([
        "python", "math_eval.py",
        "--url", "http://localhost:8000",
        "--model_name_or_path", "meta-llama/Llama-2-7b-chat-hf",
        "--data_names", "gsm8k",
        "--prompt_type", "cot",
        "--num_test_sample", "10"
    ], "Basic evaluation with local vLLM server")
    
    # Example 2: Multiple datasets with API
    run_command([
        "python", "math_eval.py",
        "--url", "http://localhost:8000",
        "--model_name_or_path", "meta-llama/Llama-2-7b-chat-hf",
        "--data_names", "gsm8k,math",
        "--prompt_type", "tool-integrated",
        "--temperature", "0.1",
        "--num_test_sample", "50"
    ], "Multiple datasets with slight temperature")
    
    # Example 3: Tool-integrated reasoning with API
    run_command([
        "python", "math_eval.py",
        "--url", "https://your-api-service.com",
        "--model_name_or_path", "your-model-name",
        "--data_names", "math",
        "--prompt_type", "tora",
        "--max_tokens_per_call", "2048",
        "--n_sampling", "3"
    ], "Tool-integrated reasoning with remote API")
    
    # Example 4: Program-assisted language modeling
    run_command([
        "python", "math_eval.py",
        "--url", "http://localhost:8000",
        "--model_name_or_path", "meta-llama/Llama-2-7b-chat-hf",
        "--data_names", "gsm8k",
        "--prompt_type", "pal",
        "--temperature", "0",
        "--save_outputs"
    ], "Program-assisted language modeling (PAL)")
    
    print(f"\n{'='*60}")
    print("Setup Instructions:")
    print("=" * 60)
    print("1. Start your API service (e.g., vLLM server):")
    print("   python -m vllm.entrypoints.openai.api_server --model MODEL_NAME --port 8000")
    print("")
    print("2. Install required dependencies:")
    print("   pip install requests")
    print("")
    print("3. Run any of the above commands (uncomment subprocess.run in the script)")
    print("")
    print("For detailed API requirements, see URL_USAGE.md")

if __name__ == "__main__":
    main()