import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import re
import pyautogui
import time
import os
import ollama
from typing import List
from ollama import Options

# Assuming ollama and necessary variables are defined
LLM_MODEL = "gemma2:2b-instruct-q8_0"
SYSTEM_PROMPT = """Your task is to generate a concise, step-by-step plan in natural language to achieve a given goal using a computer's graphical user interface (GUI). Each step should describe a specific action, such as clicking a button, selecting a menu item, or typing in a text field, and must be enclosed within <step> tags. The plan should be logical, efficient, sequential, and adaptable to different GUI layouts. Ensure that each step clearly identifies the GUI element to interact with, as the software agent will execute these steps by analyzing screenshots of the screen. Avoid any actions that could harm the system or data."""

def take_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

def prepare_inputs(image, text, processor):
    if image.mode != "RGB":
        image = image.convert("RGB")
    size = image.size
    input_text = ("What to do to execute the command? " + text.strip()).lower()
    encoding = processor(
        images=image,
        text=input_text,
        return_tensors="pt",
        do_resize=True,
    )
    encoding["image_size"] = size
    return encoding

def postprocess(text: str, image_size: tuple[int]):
    pattern = r"</s><s>(<[^>]+>|[^<\s]+)\s*([^<]*?)(<loc_\d+>.*)"
    point_pattern = r"<loc_(\d+)><loc_(\d+)>"
    match = re.search(pattern, text)
    if not match or (action := match.group(1)) != "click":
        return {
            "action": None,
            "click_point": (0, 0),
        }
    result = {
        "action": action,
    }
    try:
        location = re.findall(point_pattern, text)[0]
        if len(location) > 0:
            point = [int(loc) for loc in location]
            screen_width, screen_height = pyautogui.size()
            rescaled_point = (
                int((point[0] / 1000) * screen_width),
                int((point[1] / 1000) * screen_height)
            )
            result["click_point"] = rescaled_point
        else:
            result["click_point"] = (0, 0)
    except Exception as e:
        print(f"Error in postprocess: {str(e)}")
        result["click_point"] = (0, 0)
    return result

def execute_action(action_dict):
    if action_dict["action"] == "click" and action_dict["click_point"] != (0, 0):
        try:
            screen_width, screen_height = pyautogui.size()
            x, y = action_dict["click_point"]
            x = min(max(0, x), screen_width - 1)
            y = min(max(0, y), screen_height - 1)
            print(f"Screen size: {screen_width}x{screen_height}")
            print(f"Current mouse position: {pyautogui.position()}")
            print(f"Adjusted click position: ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click(x=x, y=y)
            return True
        except Exception as e:
            print(f"Click failed: {str(e)}")
            return False
    return False

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    response = ollama.chat(
        model=LLM_MODEL,
        options=Options(temperature=0.0),
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
    )
    return response['message']['content']

def parse_steps(plan_response: str) -> List[str]:
    step_pattern = r'<step>(.*?)</step>'
    steps = re.findall(step_pattern, plan_response, re.DOTALL)
    return [step.strip() for step in steps]

def generate_plan(goal: str) -> List[str]:
    plan_prompt = f"""
    Create a step-by-step plan to achieve this goal by indicating GUI elements to click:
    Goal: {goal}
    Enclose each step in <step></step> tags.
    Example:
    <step>Click on the Start menu</step>
    <step>Click on Settings</step>
    """
    plan_response = ask_llm(SYSTEM_PROMPT, plan_prompt)
    return parse_steps(plan_response)

def main():
    # Initialize model and processor
    print("Initializing model... (this might take a moment)")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = AutoProcessor.from_pretrained("Samsung/TinyClick", trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained("Samsung/TinyClick", trust_remote_code=True).to(device)
    
    while True:
        goal = input("\nEnter your goal (or 'quit' to exit): ")
        if goal.lower() == 'quit':
            break
        steps = generate_plan(goal)
        print(f"Generated Plan: {steps}")
        for step in steps:
            print(f"\nExecuting step: {step}")
            screenshot = take_screenshot()
            inputs = prepare_inputs(screenshot, step, processor)
            img_size = inputs.pop("image_size")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = model.generate(**inputs)
            generated_texts = processor.batch_decode(outputs, skip_special_tokens=False)
            result = postprocess(generated_texts[0], img_size)
            print("Action dictionary:", result)
            print("Executing action in 3 seconds...")
            time.sleep(3)
            if execute_action(result):
                print("Action executed successfully!")
            else:
                print("Failed to execute action.")

if __name__ == "__main__":
    main()
