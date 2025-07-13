import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from typing import List
import os
from config import settings

# Configurar la API key desde configuración
genai.configure(api_key=settings.gemini_api_key)

async def get_invoice_data_from_gemini(prompt: str, images: List[bytes]) -> dict:
    """
    Envía el prompt y las imágenes de la factura a Gemini y devuelve el JSON extraído.
    """
    try:
        # Seleccionar el modelo. 'gemini-1.5-flash' es rápido y rentable para esta tarea.
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Configurar la generación para que devuelva JSON
        generation_config = GenerationConfig(response_mime_type="application/json")
        
        # Construir el contenido multimodal: primero el texto del prompt, luego las imágenes
        content_parts = [prompt]
        for img_bytes in images:
            content_parts.append({
                "mime_type": "image/png",
                "data": img_bytes
            })

        # Realizar la llamada a la API
        response = await model.generate_content_async(
            content_parts,
            generation_config=generation_config
        )
        
        # El response.text contendrá la cadena JSON. La deserialización se hará fuera.
        # También se puede acceder al conteo de tokens para el logging
        prompt_tokens = response.usage_metadata.prompt_token_count
        completion_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count
        
        # Devolver el texto JSON y la información de uso
        return {
            "json_text": response.text,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }

    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return {"error": str(e)}