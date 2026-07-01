import json

import boto3

from app.config import settings


class BedrockLLM:
    def __init__(self):
        self.enabled = settings.use_bedrock
        self.model_id = settings.bedrock_model_id
        self.region = settings.aws_region

        self.client = None

        if self.enabled:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.region,
            )

    def generate_or_fallback(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback_text: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> str:
        if not self.enabled:
            return fallback_text

        try:
            if "anthropic.claude" in self.model_id:
                return self._invoke_claude(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            return fallback_text

        except Exception:
            return fallback_text

    def _invoke_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        response_body = json.loads(response["body"].read())

        return response_body["content"][0]["text"]