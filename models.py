from transformers import pipeline

class BaseModelWrapper:
    def __init__(self, model_name):
        self._model_name = model_name
        self._pipeline = None

    def load(self):
        raise NotImplementedError

    def run(self, input_data):
        raise NotImplementedError


class TextToImageModelWrapper(BaseModelWrapper):
    def __init__(self, model_name='runwayml/stable-diffusion-v1-5'):
        super().__init__(model_name)

    def load(self):
        if self._pipeline is None:
            from diffusers import StableDiffusionPipeline
            import torch
            # Load lighter Stable Diffusion (v1-5)
            self._pipeline = StableDiffusionPipeline.from_pretrained(self._model_name)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._pipeline = self._pipeline.to(device)

    def run(self, input_data):
        self.load()
        result = self._pipeline(input_data, num_inference_steps=20, guidance_scale=7.5)
        return result.images[0]  # return PIL image


class ImageModelWrapper(BaseModelWrapper):
    def __init__(self, model_name='google/vit-base-patch16-224'):
        super().__init__(model_name)

    def load(self):
        if self._pipeline is None:
            self._pipeline = pipeline('image-classification', model=self._model_name)

    def run(self, input_data):
        self.load()
        out = self._pipeline(input_data)
        return '\n'.join([f"{p['label']} ({p['score']:.3f})" for p in out[:3]])