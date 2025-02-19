import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel


class VertexAi:
    def __init__(self, project_id, region):
        self.vertex = vertexai.init(project=project_id, location=region)
        self.model = None

    def set_gemini_model(self, model):
        """
        Sets Gemini model to use

        Args:
            model (Str): The model type to use.
        """
        self.model = GenerativeModel(model_name=model)

    def generate_from_list_prompts(
        self, prompts: list[str], response_schema: dict = None
    ) -> list[str]:
        """Generate summaries from a list of prompts

        Args:
            prompts (list[str]):
                A list containing the prompts to be processed
            response_schema (dict): None
                A dict containing the schema for the response in JSON format

        Returns:
            list[str]:
                A list containing the generated summaries
        """
        results = []

        if response_schema:
            generation_config = GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        else:
            generation_config = GenerationConfig()

        for prompt in prompts:
            result = self.model.generate_content(
                prompt, generation_config=generation_config
            )
            results.append(result.text)

        return results
