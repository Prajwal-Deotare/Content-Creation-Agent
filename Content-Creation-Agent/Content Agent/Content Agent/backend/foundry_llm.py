import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


load_dotenv()


class FoundryLLM:

    def __init__(self):
        endpoint = os.getenv("FOUNDRY_ENDPOINT")
        model = os.getenv("FOUNDRY_MODEL")

        if not endpoint:
            raise RuntimeError("FOUNDRY_ENDPOINT is not configured.")

        if not model:
            raise RuntimeError("FOUNDRY_MODEL is not configured.")

        credential = DefaultAzureCredential()

        token_provider = get_bearer_token_provider(
            credential,
            "https://ai.azure.com/.default"
        )

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2025-04-01-preview",
            azure_ad_token_provider=token_provider
        )

        self.model = model

    def generate(self, instructions: str, user_message: str):
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_message
        )

        return response.output_text

    def generate_structured(
        self,
        instructions: str,
        user_message: str,
        schema: dict
    ):
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_message,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema["name"],
                    "strict": True,
                    "schema": schema["schema"]
                }
            }
        )

        return response.output_text