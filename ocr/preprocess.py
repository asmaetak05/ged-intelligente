import logging

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

def deskew(image):
    """Calcule l'angle de biais de l'image et la redresse (deskew) (OC-05)."""
    if cv2 is None or np is None:
        return image
    
    try:
        # Convertir en niveaux de gris
        img_np = np.array(image)
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np
            
        # Binariser pour détacher le texte
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Trouver toutes les coordonnées des pixels blancs (le texte)
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) == 0:
            return image
            
        angle = cv2.minAreaRect(coords)[-1]
        
        # Normaliser l'angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Si le biais est significatif
        if abs(angle) > 0.5 and abs(angle) < 45:
            h, w = img_np.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img_np, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            from PIL import Image
            return Image.fromarray(rotated)
    except Exception as e:
        logging.warning(f"[Preprocessing] Erreur lors du deskew : {e}")
        
    return image

def denoise(image):
    """Applique un filtre médian pour réduire le bruit (denoise) (OC-05)."""
    if cv2 is None or np is None:
        return image
    
    try:
        img_np = np.array(image)
        denoised = cv2.medianBlur(img_np, 3)
        from PIL import Image
        return Image.fromarray(denoised)
    except Exception as e:
        logging.warning(f"[Preprocessing] Erreur lors du denoise : {e}")
        
    return image

def binarize(image):
    """Seuillage adaptatif d'image (binarize) (OC-05)."""
    if cv2 is None or np is None:
        return image
        
    try:
        img_np = np.array(image)
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np
        binarized = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        from PIL import Image
        return Image.fromarray(binarized)
    except Exception as e:
        logging.warning(f"[Preprocessing] Erreur lors de la binarisation : {e}")
        
    return image
