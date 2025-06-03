import os
import json
import random
import json
import os
import numpy as np
from pathlib import Path
from typing import Iterable, Union, Any

# Global cache for prompt templates
_prompt_template_cache = {}


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    print(f"Random seed set as {seed}")


def load_jsonl(file: Union[str, Path]) -> Iterable[Any]:
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except:
                print("Error in loading:", line)
                exit()


def save_jsonl(samples, save_path):
    # ensure path
    folder = os.path.dirname(save_path)
    os.makedirs(folder, exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    print("Saved to", save_path)


def lower_keys(example):  
    new_example = {}  
    for key, value in example.items():  
        if key != key.lower():  
            new_key = key.lower()  
            new_example[new_key] = value  
        else:  
            new_example[key] = value  
    return new_example 


def load_prompt_template(prompt_type, template_path=None):
    """
    Load prompt template from file with caching.
    Only loads the template file once during runtime.
    
    Args:
        prompt_type: Type of prompt template ('glow' or 'simple')
        template_path: Optional custom path to template file
    
    Returns:
        str: The prompt template content
    """
    global _prompt_template_cache
    
    # Use custom path if provided, otherwise use default
    if template_path:
        cache_key = template_path
        file_path = template_path
    else:
        cache_key = prompt_type
        file_path = f"./prompts/{prompt_type}.txt"
    
    # Return cached template if already loaded
    if cache_key in _prompt_template_cache:
        return _prompt_template_cache[cache_key]
    
    # Load template from file
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as fp:
                template = fp.read().strip()
            _prompt_template_cache[cache_key] = template
            print(f"Loaded prompt template from {file_path}")
            return template
        else:
            print(f"Warning: prompt template file {file_path} not found")
            return ""
    except Exception as e:
        print(f"Error loading prompt template from {file_path}: {e}")
        return ""


def load_prompt(data_name, prompt_type):
    if data_name in ['gsm_hard', 'svamp', 'tabmwp', 'asdiv', 'mawps']:
        data_name = "gsm8k"
    if data_name in ['math_oai', "hungarian_exam"]:
        data_name = "math"
    if data_name in ['sat_math']:
        data_name = "mmlu_stem"
    if prompt_type in ['platypus_fs']:
        prompt_type = "cot"
    if prompt_type in ['tool-integrated']:
        prompt_type = "tora"

    if prompt_type in ['cot', 'pal', 'tora']:
        prompt_path = "./prompts/{}/{}.md".format(prompt_type, data_name)
        if not os.path.exists(prompt_path):
            prompt_path = "./prompts/{}.md".format(prompt_type)
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as fp:
                prompt = fp.read().strip() + "\n\n\n"
        else:
            print(f"Error: prompt file {prompt_path} not found")
            prompt = ""
    else:
        prompt = ""
    return prompt

def construct_prompt(example, data_name, args):
    # Base models
    if args.prompt_type in ["direct", "cot", "pal", "tool-integrated"]:
        demo_prompt = load_prompt(data_name, args.prompt_type)
        if args.prompt_type in ["direct", "cot"]:
            if data_name in ["minerva_math", "math", "math_oai", "mmlu_stem", "sat_math", "mathqa", "hungarian_exam"]:
                context = f"Problem:\n{example['question']}\nSolution:"
            else:
                context = f"Question: {example['question']}\nAnswer:"
            full_prompt = demo_prompt + context
        elif args.prompt_type == "pal":
            context = f"Question: {example['question']}"
            full_prompt = demo_prompt + context
        elif args.prompt_type in ['tool-integreted']:
            context = f"Question: {example['question']}\n\nSolution:"
            full_prompt = demo_prompt + context

    # SFT models
    elif args.prompt_type in ['self-instruct', 'tora']:
        full_prompt = f"<|user|>\n{example['question']}\n<|assistant|>\n"
    elif args.prompt_type in ['self-instruct-boxed']:
        full_prompt = f"<|user|>\n{example['question']}\nEnclose the final answer using \\boxed{{}}.\n<|assistant|>\n"
    elif args.prompt_type == "wizard_zs":
        full_prompt = (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n{instruction}\n\n### Response: Let's think step by step."
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "deepseek-math":
        full_prompt = (
            "User: {instruction}\nPlease reason step by step, "
            "and put your final answer within \\boxed{{}}.\n\nAssistant:"
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "kpmath":
        full_prompt = (
            'User: Please reason step by step and put your final answer at the end '
            'with "The answer is: ".\n\n{instruction}\n\nAssistant:'
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "glow":
        # Get custom template path if provided in args
        template_path = getattr(args, 'glow_template_path', None)
        template = load_prompt_template("glow", template_path)
        if template:
            # Replace placeholder with actual question
            full_prompt = template.replace("#QUERY#", example['question'])
        else:
            # Fallback to hardcoded template if file loading fails
            full_prompt = (
                """You are an assistant that possesses expertise in the art of condensing the user's search results into a concise chapter, tailored specifically to address the user's query. It's called TLDR.
- User will provide the search query and search results obtained from the search engine.
- You should have a deep understanding of user's query and catch user's intent.
- You must summarize a **concise and accurate** chapter to address user's intent **only** from the given search results. The chapter is to prioritize **brevity** over depth of information.
- To better understand your chapter content for user, you should choose the best data format to display them, such as table format, bullet format or paragraph format.
- Output the chapter **in the same language as the user's query**. If the user's query is in English, you should generate your response in English. If the user's query is in 中文, you should generate your response in 中文.

----
You should generate chapter step by step:
- Step 1: understand user's query: "{instruction}".
- Step 2: understand the guideline of generated document: "".
- Step 3: read above documents carefully, and aware of all the numerical values, dates, names, prices etc. in the search results.
- Step 4: generate **the most concise and accurate** chapter content that addresses user's intent **only from** the given search results. You must only generate the key answers but not any backgrounds and explanations. You are to prioritize **brevity** over depth of information.
- Step 5: choose a best format to show the chapter content. If it is structured, numerical or side-by-side, you should use Table Format, otherwise use Bullets Format or Paragraph Format. You **must not** treat reference citation and image citation as a separate column in Table Format.
- Step 6: use <~~~> to highlight the most import content in one line to directly answer the query.
- Step 7: The time at the start of this search is 1 Jan 2025, please use the newest data first.
- Step 8: use [REFUSAL] to refuse answer query when grounding data is not enough or irrelevant to query.
----
Following steps above, the chapter that can address user's query is:"""
            )
            full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "simple":
        # Get custom template path if provided in args
        template_path = getattr(args, 'simple_template_path', None)
        template = load_prompt_template("simple", template_path)
        if template:
            # Replace placeholder with actual question
            full_prompt = template.replace("#QUERY#", example['question'])
        else:
            # Fallback to hardcoded template if file loading fails
            full_prompt = (
                """# Instructions
Given a math question, please solve the problem and output the final answer.
* You should provide multi-step thinking and calculations, not just the final answer.
* You should provide solutions in natural language, as opposed to pure math expressions.
* The final output should be like: multiple steps of reasoning "####" final answer
# Example
Question: Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?
Answer:
Weng earns 12/60 = 0.2 per minute.
Working 50 minutes, she earned 0.2 x 50 = 10.
#### 10
# Task
Question: {instruction}
Answer:"""
            )
            full_prompt = full_prompt.format(instruction=example['question'])
    else:
        raise NotImplementedError(args.prompt_type)
    return full_prompt

key_map = {
    "gt": "Ground Truth",
    "pred": "Prediction",
    "gt_cot": "Reference CoT",
    "score": "Score",
}

def show_sample(sample, print_all_preds=False):
    print("=="*20)
    for key in ["idx", "type", "level", "dataset"]:
        if key in sample:
            # capitalize
            print("{}: {}".format(key[0].upper() + key[1:], sample[key]))
    print("Question:", repr(sample['question']))
    if 'code' in sample:
        if print_all_preds:
            for code in sample['code']:
                print('-'*20)
                print("code:", code)
            print("Execution:", sample['report'])
        else:
            print("Solution:\n", sample['code'][0])
            print("Execution:", sample['report'][0])
    if 'pred' in sample:
        print("Prediction:", repr(sample['pred'][0]))
    for key in ["gt", "score", "unit", "gt_cot"]:
        if key in sample:
            _key  = key_map.get(key, key)
            print("{}: {}".format(_key, repr(sample[key])))
    print()
