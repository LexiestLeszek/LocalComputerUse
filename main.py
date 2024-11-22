
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import re
import pyautogui
import time

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
            
            # Get actual screen size
            screen_width, screen_height = pyautogui.size()
            
            # Scale points based on screen size instead of image size
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
            
            # Click
            pyautogui.click(x=x, y=y)
            return True
            
        except Exception as e:
            print(f"Click failed: {str(e)}")
            return False
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

        text = input("\nEnter your command (or 'quit' to exit): ")
        
        if text.lower() == 'quit':
            break
            
        print("Taking screenshot...")
        
        screenshot = take_screenshot()
        
        inputs = prepare_inputs(screenshot, text, processor)
        img_size = inputs.pop("image_size")
        
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        print("Analyzing screenshot...")
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
