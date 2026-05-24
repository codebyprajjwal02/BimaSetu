import os
import sys
import glob
import cv2
import numpy as np
import torch
import torchvision.models as tv_models

sys.path.append(r"c:\Users\Niru\OneDrive\my progress\Desktop\bimasetu\backend")

def get_imagenet_model():
    weights = tv_models.MobileNet_V2_Weights.DEFAULT
    model = tv_models.mobilenet_v2(weights=weights)
    model.eval()
    categories = weights.meta["categories"]
    return model, categories

def analyze_deeply():
    model, categories = get_imagenet_model()
    uploads_dir = r"c:\Users\Niru\OneDrive\my progress\Desktop\bimasetu\backend\static\uploads"
    image_paths = glob.glob(os.path.join(uploads_dir, "*.jpg"))
    
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    print(f"Found {len(image_paths)} images to inspect.")
    print("=" * 100)

    for path in sorted(image_paths):
        filename = os.path.basename(path)
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            print(f"{filename}: Failed to load image")
            continue
            
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        total_px = img_bgr.shape[0] * img_bgr.shape[1]

        # 1. Color ratios
        green_mask = cv2.inRange(hsv, (30, 20, 20), (90, 255, 255))
        green_ratio = (green_mask.sum() / 255) / total_px

        brown_mask = cv2.inRange(hsv, (10, 25, 20), (30, 255, 255))
        brown_ratio = (brown_mask.sum() / 255) / total_px

        skin_mask = cv2.inRange(hsv, (0, 20, 60), (20, 150, 255))
        skin_ratio = (skin_mask.sum() / 255) / total_px

        # 2. Textures
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        edges = cv2.Canny(gray, 30, 120)
        edge_ratio = np.sum(edges > 0) / total_px

        # Standard deviations of hue
        green_pixels = hsv[green_mask > 0]
        green_hue_std = np.std(green_pixels[:, 0]) if len(green_pixels) > 500 else 10.0
        
        brown_pixels = hsv[brown_mask > 0]
        brown_hue_std = np.std(brown_pixels[:, 0]) if len(brown_pixels) > 500 else 10.0

        # ImageNet Inference
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (224, 224)).astype(np.float32) / 255.0
        img_norm = (img_resized - mean) / std
        tensor = torch.from_numpy(img_norm.transpose(2, 0, 1)).unsqueeze(0)

        with torch.no_grad():
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1).squeeze().numpy()

        top5_indices = np.argsort(probs)[-5:][::-1]
        top5_predictions = [(categories[idx], float(probs[idx])) for idx in top5_indices]

        print(f"File: {filename}")
        print(f"  HSV stats: Green={green_ratio:.3f} (std={green_hue_std:.2f}), Brown={brown_ratio:.3f} (std={brown_hue_std:.2f}), Nature={green_ratio+brown_ratio:.3f}, Skin={skin_ratio:.3f}")
        print(f"  Texture  : Laplacian={laplacian_var:.2f}, Edge ratio={edge_ratio:.3f}")
        print(f"  Top 5 Predictions:")
        for name, prob in top5_predictions:
            print(f"    - {name}: {prob:.4f}")
        print("-" * 100)

if __name__ == "__main__":
    analyze_deeply()
