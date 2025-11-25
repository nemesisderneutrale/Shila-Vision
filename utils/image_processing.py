"""Bildverarbeitungs-Utilities für bessere Tag-Qualität.
Basierend auf dbimutils.py aus stable-diffusion-webui-wd14-tagger."""

import cv2
import numpy as np
from PIL import Image


def fill_transparent(image: Image.Image, color='WHITE'):
    """
    Konvertiert transparente Bereiche zu weißem Hintergrund.
    
    Args:
        image: PIL Image
        color: Hintergrundfarbe ('WHITE' oder 'BLACK')
    
    Returns:
        PIL Image mit RGB-Modus
    """
    image = image.convert('RGBA')
    bg_color = (255, 255, 255) if color == 'WHITE' else (0, 0, 0)
    new_image = Image.new('RGBA', image.size, bg_color)
    new_image.paste(image, mask=image)
    image = new_image.convert('RGB')
    return image


def resize(pic: Image.Image, size: int, keep_ratio=True) -> Image.Image:
    """
    Resized ein Bild auf die gewünschte Größe.
    
    Args:
        pic: PIL Image
        size: Zielgröße
        keep_ratio: Ob Seitenverhältnis beibehalten werden soll
    
    Returns:
        Resized PIL Image
    """
    if not keep_ratio:
        target_size = (size, size)
    else:
        min_edge = min(pic.size)
        target_size = (
            int(pic.size[0] / min_edge * size),
            int(pic.size[1] / min_edge * size),
        )
    
    # Runde auf Vielfache von 4 (für manche Modelle wichtig)
    target_size = (target_size[0] & ~3, target_size[1] & ~3)
    
    return pic.resize(target_size, resample=Image.Resampling.LANCZOS)


def smart_imread(img_path: str, flag=cv2.IMREAD_UNCHANGED):
    """
    Liest ein Bild und konvertiert es zu 24-bit falls nötig.
    
    Args:
        img_path: Pfad zum Bild
        flag: OpenCV Read-Flag
    
    Returns:
        OpenCV Image (BGR)
    """
    if img_path.endswith(".gif"):
        img = Image.open(img_path)
        img = img.convert("RGB")
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    else:
        img = cv2.imread(img_path, flag)
    return img


def smart_24bit(img):
    """
    Konvertiert ein Bild zu 24-bit falls nötig.
    
    Args:
        img: OpenCV Image (numpy array)
    
    Returns:
        24-bit BGR Image
    """
    if img.dtype is np.dtype(np.uint16):
        img = (img / 257).astype(np.uint8)
    
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        trans_mask = img[:, :, 3] == 0
        img[trans_mask] = [255, 255, 255, 255]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


def make_square(img, target_size):
    """
    Macht ein Bild quadratisch durch Padding.
    
    Args:
        img: OpenCV Image (numpy array, BGR)
        target_size: Mindestgröße für das quadratische Bild
    
    Returns:
        Quadratisches OpenCV Image
    """
    old_size = img.shape[:2]
    desired_size = max(old_size)
    desired_size = max(desired_size, target_size)
    
    delta_w = desired_size - old_size[1]
    delta_h = desired_size - old_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    
    color = [255, 255, 255]  # Weiß
    new_im = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return new_im


def smart_resize(img, size):
    """
    Resized ein Bild intelligent (verschiedene Interpolation je nach Größe).
    
    Args:
        img: OpenCV Image (numpy array, BGR)
        size: Zielgröße
    
    Returns:
        Resized OpenCV Image
    """
    # Annahme: Bild wurde bereits durch make_square quadratisch gemacht
    if img.shape[0] > size:
        # Verkleinern: INTER_AREA für bessere Qualität
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    elif img.shape[0] < size:
        # Vergrößern: INTER_CUBIC für bessere Qualität
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
    return img


def preprocess_for_wd14(image: Image.Image, target_size: int = 448) -> np.ndarray:
    """
    Vollständiges Preprocessing für WD14 Tagger Modelle.
    Kombiniert alle Schritte für optimale Tag-Qualität.
    Basierend auf der Original-Implementierung von SmilingWolf.
    
    Args:
        image: PIL Image
        target_size: Zielgröße (Standard: 448 für WD14)
    
    Returns:
        Preprocessed numpy array (BGR, float32, shape: (1, H, W, 3))
        WICHTIG: Keine ImageNet-Normalisierung! Das Modell erwartet [0, 255] Werte.
    """
    # 1. Alpha zu Weiß konvertieren
    image = fill_transparent(image, color='WHITE')
    
    # 2. PIL zu numpy (RGB)
    img_array = np.array(image)
    
    # 3. RGB zu BGR (OpenCV Format)
    img_bgr = img_array[:, :, ::-1]  # RGB zu BGR
    
    # 4. Quadratisch machen
    img_bgr = make_square(img_bgr, target_size)
    
    # 5. Smart Resize
    img_bgr = smart_resize(img_bgr, target_size)
    
    # 6. Zu float32 konvertieren (WICHTIG: Keine Normalisierung auf [0,1]!)
    # Das Modell erwartet [0, 255] Werte in float32
    img_bgr = img_bgr.astype(np.float32)
    
    # 7. Batch-Dimension hinzufügen
    img_bgr = np.expand_dims(img_bgr, 0)  # (1, H, W, 3)
    
    return img_bgr

