# Using External API with --url Parameter

The math evaluation harness now supports using external LLM services that expose OpenAI-compatible REST APIs via the `--url` parameter.

## Usage

When you want to use an external service instead of a local model, add the `--url` parameter:

```bash
python math_eval.py --url http://localhost:8000 --data_names gsm8k --prompt_type cot
```

## API Requirements

The external service must:

1. **Follow OpenAI Chat Completion Protocol**: The service should expose a `/v1/chat/completions` endpoint
2. **Accept POST requests** with the following JSON payload:
   ```json
   {
     "model": "your-model-name",
     "messages": [
       {
         "role": "user",
         "content": "Your math problem prompt here"
       }
     ],
     "max_tokens": 1024,
     "temperature": 0,
     "top_p": 1,
     "stream": false,
     "stop": ["</s>", "\n\nQuestion:"]
   }
   ```
   
   Note: The `model` field will be set to the value of `--model_name_or_path` argument.

3. **Return responses** in the OpenAI format:
   ```json
   {
     "choices": [
       {
         "message": {
           "content": "Generated response text"
         }
       }
     ]
   }
   ```

## Examples

### Local vLLM Server
If you're running a vLLM server locally:
```bash
# Start vLLM server (in another terminal)
python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-chat-hf --port 8000

# Run evaluation (model name will be passed to the API)
python math_eval.py --url http://localhost:8000 --model_name_or_path meta-llama/Llama-2-7b-chat-hf --data_names gsm8k --temperature 0.1
```

### Remote API Service
For a remote service:
```bash
python math_eval.py --url https://your-api-service.com --model_name_or_path your-model-name --data_names math --prompt_type tora
```

## Behavior Changes

When `--url` is specified:

1. **No local model loading**: The system skips loading local models (no VLLM or HuggingFace model loading)
2. **API calls**: All generation requests are sent to the specified URL endpoint
3. **Same evaluation flow**: All other evaluation logic remains the same (prompt construction, result parsing, etc.)

## Parameters Supported

All existing parameters work with `--url`:

- `--temperature`: Controls randomness in generation
- `--top_p`: Controls nucleus sampling
- `--max_tokens_per_call`: Maximum tokens to generate per request
- `--n_sampling`: Number of samples per question (each will be a separate API call)
- All prompt types: `cot`, `pal`, `tool-integrated`, `tora`
- All datasets: `gsm8k`, `math`, `asdiv`, etc.

## Error Handling

The system handles common API errors:
- Network timeouts (120 second timeout per request)
- HTTP errors (non-200 status codes)
- Malformed JSON responses
- Missing response fields

Failed requests will result in empty responses and be logged to the console.