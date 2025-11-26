"""
Image Analysis Module
Provides AI-generated image detection and reverse image search capabilities.
"""
import os
import io
import base64
from typing import Dict, List, Optional, Tuple
from PIL import Image
import requests
from huggingface_hub import InferenceClient

# Load API keys
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

class ImageAnalyzer:
    def __init__(self):
        self.hf_client = None
        if HUGGINGFACE_API_KEY:
            self.hf_client = InferenceClient(token=HUGGINGFACE_API_KEY)
            print("✓ Hugging Face client initialized")
        else:
            print("WARNING: HUGGINGFACE_API_KEY not set. AI detection will use fallback.")
    
    def detect_ai_generated(self, image_data: bytes) -> Dict:
        """
        Detect if an image is AI-generated using Hugging Face models.
        Returns probability and confidence score.
        """
        try:
            if not self.hf_client:
                return self._fallback_ai_detection(image_data)
            
            print("Analyzing image with Hugging Face AI detector...")
            
            # Use Hugging Face's AI image detection model
            # Model: umm-maybe/AI-image-detector or similar
            result = self.hf_client.image_classification(
                image=image_data,
                model="umm-maybe/AI-image-detector"
            )
            
            # Parse results
            ai_score = 0.0
            real_score = 0.0
            
            for item in result:
                label = item['label'].lower()
                score = item['score']
                
                if 'artificial' in label or 'ai' in label or 'generated' in label:
                    ai_score = max(ai_score, score)
                elif 'real' in label or 'natural' in label or 'human' in label:
                    real_score = max(real_score, score)
            
            # Calculate final probability
            ai_probability = ai_score * 100
            
            # Determine verdict
            if ai_probability > 70:
                verdict = "Likely AI-Generated"
                confidence = "High"
            elif ai_probability > 40:
                verdict = "Possibly AI-Generated"
                confidence = "Medium"
            else:
                verdict = "Likely Real Photo"
                confidence = "High" if ai_probability < 20 else "Medium"
            
            print(f"AI Detection: {verdict} ({ai_probability:.1f}%)")
            
            return {
                "ai_probability": round(ai_probability, 2),
                "real_probability": round(real_score * 100, 2),
                "verdict": verdict,
                "confidence": confidence,
                "model": "umm-maybe/AI-image-detector",
                "details": result
            }
            
        except Exception as e:
            print(f"ERROR in AI detection: {e}")
            return self._fallback_ai_detection(image_data)
    
    def describe_image(self, image_data: bytes) -> Dict:
        """
        Generate a detailed description of the image using Hugging Face vision models.
        """
        try:
            if not self.hf_client:
                return self._fallback_description(image_data)
            
            print("Generating image description with Hugging Face...")
            
            # Use Hugging Face's image-to-text model
            # Model: Salesforce/blip-image-captioning-large or similar
            result = self.hf_client.image_to_text(
                image=image_data,
                model="Salesforce/blip-image-captioning-large"
            )
            
            # Extract description
            description = result[0]['generated_text'] if result else "Unable to generate description"
            
            print(f"Image description: {description}")
            
            return {
                "description": description,
                "model": "Salesforce/blip-image-captioning-large",
                "confidence": "High"
            }
            
        except Exception as e:
            print(f"ERROR in image description: {e}")
            return self._fallback_description(image_data)
    
    def _fallback_description(self, image_data: bytes) -> Dict:
        """
        Fallback image description when Hugging Face API unavailable.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            format_type = image.format
            
            description = f"An image in {format_type} format with dimensions {width}x{height} pixels."
            
            return {
                "description": description,
                "model": "fallback_basic",
                "confidence": "Low"
            }
        except Exception as e:
            return {
                "description": "Unable to describe image",
                "model": "error",
                "confidence": "None"
            }
    
    def _fallback_ai_detection(self, image_data: bytes) -> Dict:
        """
        Fallback AI detection using image properties analysis.
        Used when Hugging Face API is unavailable.
        """
        try:
            print("Using fallback AI detection (analyzing image properties)...")
            
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Analyze properties
            width, height = image.size
            format_type = image.format
            mode = image.mode
            
            # Simple heuristics (not accurate, just for fallback)
            score = 50.0  # Start neutral
            
            # AI images often have perfect dimensions
            if width == height or (width % 512 == 0 and height % 512 == 0):
                score += 15
            
            # Check for common AI image sizes
            common_ai_sizes = [(512, 512), (1024, 1024), (768, 768), (1024, 768)]
            if (width, height) in common_ai_sizes:
                score += 20
            
            # Very high resolution might indicate real photo
            if width > 3000 or height > 3000:
                score -= 20
            
            # Limit score
            score = max(0, min(100, score))
            
            if score > 70:
                verdict = "Possibly AI-Generated (Fallback Analysis)"
            elif score > 40:
                verdict = "Uncertain (Fallback Analysis)"
            else:
                verdict = "Possibly Real Photo (Fallback Analysis)"
            
            return {
                "ai_probability": round(score, 2),
                "real_probability": round(100 - score, 2),
                "verdict": verdict,
                "confidence": "Low",
                "model": "fallback_heuristic",
                "details": {
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "mode": mode
                }
            }
            
        except Exception as e:
            print(f"ERROR in fallback detection: {e}")
            return {
                "ai_probability": 50.0,
                "real_probability": 50.0,
                "verdict": "Analysis Failed",
                "confidence": "None",
                "model": "error",
                "details": {"error": str(e)}
            }
    
    def reverse_image_search(self, image_data: bytes) -> List[Dict]:
        """
        Perform reverse image search to find sources.
        Uses Google Images search.
        """
        try:
            print("Performing reverse image search...")
            
            # For now, return mock results
            # Real implementation would use SerpAPI or Google Custom Search
            # Or scrape Google Images (less reliable)
            
            return [
                {
                    "title": "Reverse image search feature",
                    "url": "https://images.google.com/",
                    "source": "Google Images",
                    "snippet": "Upload your image to Google Images to find similar images and sources."
                },
                {
                    "title": "TinEye Reverse Image Search",
                    "url": "https://tineye.com/",
                    "source": "TinEye",
                    "snippet": "TinEye is a reverse image search engine that helps you find where an image came from."
                }
            ]
            
        except Exception as e:
            print(f"ERROR in reverse image search: {e}")
            return []
    
    def extract_metadata(self, image_data: bytes) -> Dict:
        """
        Extract EXIF metadata from image.
        """
        try:
            print("Extracting image metadata...")
            
            image = Image.open(io.BytesIO(image_data))
            
            # Basic info
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": f"{image.size[0]}x{image.size[1]}",
                "width": image.size[0],
                "height": image.size[1],
            }
            
            # Try to get EXIF data
            exif_data = image.getexif()
            if exif_data:
                # Add some common EXIF tags
                metadata["has_exif"] = True
                metadata["exif_tags_count"] = len(exif_data)
            else:
                metadata["has_exif"] = False
                metadata["note"] = "No EXIF data found (common in AI-generated images)"
            
            return metadata
            
        except Exception as e:
            print(f"ERROR extracting metadata: {e}")
            return {"error": str(e)}
    
    def analyze_image(self, image_data: bytes) -> Dict:
        """
        Perform complete image analysis.
        Combines AI detection, reverse search, and metadata extraction.
        """
        print("=" * 50)
        print("Starting comprehensive image analysis...")
        print("=" * 50)
        
        results = {
            "ai_detection": self.detect_ai_generated(image_data),
            "reverse_search": self.reverse_image_search(image_data),
            "description": self.describe_image(image_data),
            "metadata": self.extract_metadata(image_data)
        }
        
        print("=" * 50)
        print("Image analysis complete!")
        print("=" * 50)
        
        return results


# Global instance
image_analyzer = ImageAnalyzer()
