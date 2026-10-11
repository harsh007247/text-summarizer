"""
================================================================================
Prediction Pipeline for PEGASUS Text Summarization
================================================================================
Loads the fine-tuned PEGASUS model and tokenizer from the configured checkpoint.
Provides generation with custom summary length parameters and GPU/CPU support.
================================================================================
"""

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from textsummarizer.config.configuration import ConfigurationManager
from textsummarizer.logging import logger


class PredictionPipeline:
    """
    Prediction Pipeline for PEGASUS Text Summarization.
    Loads the trained model and tokenizer from paths defined in configuration.
    Supports GPU acceleration when CUDA is available and CPU fallback.
    """
    def __init__(self, model=None, tokenizer=None):
        self.config = ConfigurationManager().get_model_evaluation_config()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Reuse existing model/tokenizer if provided
        if tokenizer is not None and model is not None:
            self.tokenizer = tokenizer
            self.model = model.to(self.device)
        else:
            logger.info(f"Loading tokenizer from: {self.config.tokenizer_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.config.tokenizer_path))
            
            logger.info(f"Loading PEGASUS model from: {self.config.model_path} onto {self.device}")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(str(self.config.model_path)).to(self.device)
            
        self.model.eval()

    def predict(
        self,
        text: str,
        max_length: int = 128,
        min_length: int = 20,
        num_beams: int = 8,
        length_penalty: float = 0.8
    ) -> str:
        """
        Generate a summary for the provided input text.
        
        Args:
            text (str): Input text / dialogue to summarize.
            max_length (int): Maximum generation token length.
            min_length (int): Minimum generation token length.
            num_beams (int): Number of beams for beam search.
            length_penalty (float): Exponential penalty to length.
            
        Returns:
            str: Decoded summary text.
        """
        inputs = self.tokenizer(
            text,
            max_length=1024,
            truncation=True,
            padding=False,
            return_tensors="pt"
        )
        
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        gen_kwargs = {
            "max_length": int(max_length),
            "num_beams": int(num_beams),
            "length_penalty": float(length_penalty),
        }
        
        # Ensure min_length is positive and does not exceed max_length
        if min_length is not None and int(min_length) > 0:
            gen_kwargs["min_length"] = min(int(min_length), int(max_length))

        with torch.no_grad():
            summary_ids = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                **gen_kwargs
            )

        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

        return summary.strip()


# Global singleton instance for standalone function usage
_default_pipeline = None

def get_prediction_pipeline() -> PredictionPipeline:
    """Returns a singleton instance of PredictionPipeline."""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = PredictionPipeline()
    return _default_pipeline

def predict(
    text: str,
    max_length: int = 128,
    min_length: int = 20,
    num_beams: int = 8,
    length_penalty: float = 0.8
) -> str:
    """Convenience function to generate summary directly."""
    p = get_prediction_pipeline()
    return p.predict(
        text=text,
        max_length=max_length,
        min_length=min_length,
        num_beams=num_beams,
        length_penalty=length_penalty
    )