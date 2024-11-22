
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import re
import pyautogui
import time

def take_screenshot():
    """Take a screenshot and return it as PIL Image"""
    screenshot = pyautogui.screenshot()
    return screenshot

def prepare_inputs(image, text, processor):
    """Prepare inputs for the model"""
    # Convert to RGB if not already
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
    """Process model output into action dictionary"""
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

            rescaled_point = (
                int((point[0] / 1000) * image_size[0]),
                int((point[1] / 1000) * image_size[1]),
            )

            result["click_point"] = rescaled_point
        else:
            result["click_point"] = (0, 0)

    except Exception:
        result["click_point"] = (0, 0)

    return result

def execute_action(action_dict):
    """Execute the action based on the dictionary"""
    if action_dict["action"] == "click" and action_dict["click_point"] != (0, 0):
        x, y = action_dict["click_point"]
        pyautogui.click(x, y)
        return True
    return False

def main():
    # Initialize model and processor
    print("Initializing model... (this might take a moment)")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = AutoProcessor.from_pretrained(
        "Samsung/TinyClick", trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        "Samsung/TinyClick",
        trust_remote_code=True,
    ).to(device)
    
    while True:
        # Get command from user
        text = input("\nEnter your command (or 'quit' to exit): ")
        
        if text.lower() == 'quit':
            break
            
        # Give user time to prepare the screen
        print("Taking screenshot in 3 seconds...")
        time.sleep(3)
        
        # Take screenshot
        screenshot = take_screenshot()
        
        # Prepare inputs
        inputs = prepare_inputs(screenshot, text, processor)
        img_size = inputs.pop("image_size")
        
        # Move inputs to device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate prediction
        print("Analyzing screenshot...")
        outputs = model.generate(**inputs)
        
        # Process outputs
        generated_texts = processor.batch_decode(outputs, skip_special_tokens=False)
        result = postprocess(generated_texts[0], img_size)
        
        # Print result
        print("Action dictionary:", result)
        
        # Execute action
        print("Executing action...")
        if execute_action(result):
            print("Action executed successfully!")
        else:
            print("Failed to execute action.")

if __name__ == "__main__":
    main()