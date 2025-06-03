# Prompt Template Loading with Caching

This document describes the enhanced prompt template loading functionality for `glow` and `simple` prompt types.

## Overview

The `utils.py` file has been updated to support loading prompt templates from files with a caching mechanism that ensures templates are loaded only once during runtime, improving performance.

## Features

- **File-based templates**: `glow` and `simple` prompt types now load templates from external files
- **Caching mechanism**: Templates are loaded only once and cached for subsequent use
- **Custom template paths**: File paths can be specified via command-line arguments
- **Fallback support**: If file loading fails, the system falls back to hardcoded templates
- **Placeholder replacement**: Templates use `#QUERY#` placeholder that gets replaced with the actual question

## Usage

### Default Template Loading

By default, the system will load templates from:
- `./prompts/glow.txt` for `--prompt_type glow`
- `./prompts/simple.txt` for `--prompt_type simple`

```bash
python math_eval.py --prompt_type glow --data_names gsm8k
python math_eval.py --prompt_type simple --data_names math
```

### Custom Template Paths

You can specify custom template file paths using the new command-line arguments:

```bash
# Use custom glow template
python math_eval.py --prompt_type glow --glow_template_path ./custom_prompts/my_glow.txt

# Use custom simple template
python math_eval.py --prompt_type simple --simple_template_path ./custom_prompts/my_simple.txt
```

### Template File Format

Template files should contain the prompt text with `#QUERY#` as a placeholder for the question:

**Example glow template:**
```
You are an assistant that helps with search queries.
User query: #QUERY#
Please provide a response.
```

**Example simple template:**
```
# Instructions
Given a math question, solve it step by step.

Question: #QUERY#
Answer:
```

## Implementation Details

### Caching Mechanism

- Templates are stored in a global cache dictionary `_prompt_template_cache`
- Cache keys are either the prompt type (for default paths) or the full file path (for custom paths)
- Once loaded, templates are reused without re-reading the file

### New Command-Line Arguments

Added to `math_eval.py`:
- `--glow_template_path`: Custom path to glow prompt template file
- `--simple_template_path`: Custom path to simple prompt template file

### New Functions

**`load_prompt_template(prompt_type, template_path=None)`**
- Loads prompt template from file with caching
- Parameters:
  - `prompt_type`: Type of prompt ('glow' or 'simple')
  - `template_path`: Optional custom path to template file
- Returns: Template content as string

### Error Handling

- If a template file doesn't exist, a warning is printed and an empty string is returned
- The system falls back to hardcoded templates if file loading fails
- File reading errors are caught and logged

## Performance Benefits

1. **Reduced I/O**: Template files are read only once per execution
2. **Memory efficiency**: Templates are shared across multiple prompt constructions
3. **Fast access**: Cached templates provide immediate access after first load

## Backward Compatibility

The changes are fully backward compatible:
- Existing code continues to work without modification
- Hardcoded templates serve as fallbacks
- Other prompt types (`cot`, `pal`, etc.) are unaffected