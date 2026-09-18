import json

from foundry_llm import FoundryLLM
from models import (
    ContentRequest,
    ContentOption,
    ContentSession
)
from prompts import CONTENT_AGENT_INSTRUCTIONS


CONTENT_OPTIONS_SCHEMA = {
    "name": "content_options",
    "schema": {
        "type": "object",
        "properties": {
            "options": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "enum": ["A", "B", "C"]
                        },
                        "title": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "id",
                        "title",
                        "content"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["options"],
        "additionalProperties": False
    }
}


class ContentAgent:

    def __init__(self):
        self.llm = FoundryLLM()

    def generate_options(
        self,
        request: ContentRequest
    ) -> ContentSession:

        session = ContentSession(
            state="GENERATING",
            request=request
        )

        user_prompt = f"""
Create three content options using these requirements.

TOPIC:
{request.topic}

PLATFORM:
{request.platform}

AUDIENCE:
{request.audience}

MOOD:
{request.mood}

LENGTH:
{request.length}

GOAL:
{request.goal}

Generate exactly three meaningfully different options:
A, B and C.

Do not invent real-world experiences, statistics, studies,
testimonials, quotes, or events.
"""

        result = self.llm.generate_structured(
            instructions=CONTENT_AGENT_INSTRUCTIONS,
            user_message=user_prompt,
            schema=CONTENT_OPTIONS_SCHEMA
        )

        data = json.loads(result)

        session.options = [
            ContentOption(
                id=option["id"],
                title=option["title"],
                content=option["content"]
            )
            for option in data["options"]
        ]

        session.state = "OPTIONS_READY"

        return session

    def select_option(
        self,
        session: ContentSession,
        option_id: str
    ):

        option_id = option_id.upper()

        option = next(
            (
                option
                for option in session.options
                if option.id == option_id
            ),
            None
        )

        if not option:
            raise ValueError(
                f"Option {option_id} does not exist."
            )

        session.selected_option = option_id
        session.current_content = option.content
        session.state = "OPTION_SELECTED"

        return session

    def revise(
        self,
        session: ContentSession,
        revision_request: str
    ):

        if not session.current_content:
            raise ValueError(
                "No content has been selected for revision."
            )

        session.state = "REVISING"

        user_prompt = f"""
Revise the following content.

ORIGINAL REQUEST:

Topic:
{session.request.topic}

Platform:
{session.request.platform}

Audience:
{session.request.audience}

Mood:
{session.request.mood}

Length:
{session.request.length}

Goal:
{session.request.goal}


CURRENT CONTENT:

{session.current_content}


REVISION REQUEST:

{revision_request}


IMPORTANT:

Preserve the original requirements.

Only make changes that are relevant to the
revision request.

Do not fabricate facts, experiences, statistics,
studies, testimonials, quotes, or events.

Return only the revised content.
"""

        revised_content = self.llm.generate(
            instructions=CONTENT_AGENT_INSTRUCTIONS,
            user_message=user_prompt
        )

        session.current_content = revised_content.strip()
        session.revision_count += 1
        session.state = "REVISED"

        return session

    def approve(
        self,
        session: ContentSession
    ):

        if not session.current_content:
            raise ValueError(
                "There is no content to approve."
            )

        session.approved = True
        session.state = "READY_TO_SAVE"

        return session