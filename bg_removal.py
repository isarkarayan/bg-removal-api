import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from model.u2net import U2NET  # Import the U^2-Net model

# Load the pre-trained U^2-Net model
def load_model(model_path):
    net = U2NET(3, 1)
    net.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    net.eval()
    return net

# Preprocess the input image
def preprocess_image(image):
    image_transform = transforms.Compose([
        transforms.Resize((320, 320)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = image_transform(image).unsqueeze(0)
    return image

# Remove the background
def remove_background(net, image):
    with torch.no_grad():
        output = net(image)
    output = output.squeeze().cpu().numpy()
    output = (output * 255).astype(np.uint8)
    mask = Image.fromarray(output).resize((image.shape[2], image.shape[3]))
    return mask

# Combine the mask and original image
def apply_mask(image, mask):
    image = image.convert("RGBA")
    mask = mask.convert("L")
    image.putalpha(mask)
    return image

# Main function
def process_image(image_path, output_path):
    net = load_model("u2net.pth")
    image = Image.open(image_path).convert("RGB")
    input_image = preprocess_image(image)
    mask = remove_background(net, input_image)
    result = apply_mask(image, mask)
    result.save(output_path, "PNG")