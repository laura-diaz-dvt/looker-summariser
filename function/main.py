import json
import os
import time

import flask

from core.models import DashboardWebhook
from core.models import SummaryResponseSchema
from core.usecases import (
    convert_dict_to_text,
    generate_prompts_from_queries,
    get_dashboard_id_from_url,
)
from services.cloud_storage.cloud_storage import CloudStorageBucket
from services.cloud_logging.cloud_logging import Logger
from services.google_chat.google_chat import GoogleChat
from services.looker.looker import Looker
from services.slack.slack import Slack
from services.teams.teams import Teams
from services.vertexai.vertexai import VertexAi

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
PDF_BUCKET = os.getenv("PDF_BUCKET")
PROMPT_BUCKET = os.getenv("PROMPT_BUCKET")
K_REVISION = os.getenv("K_REVISION")

app = flask.Flask(__name__)
logger = Logger(PROJECT_ID)


@app.route("/", methods=["POST"])
def summarise_dashboard():
    """
    Processes the scheduled plan received from Looker.
    The function reads in the scheduled plan data and retrieves additional data from the Looker API.
    With this data it creates a summary of each tile in the dashboard, which at the end it will fuse together and send to the set channels.

    Args:
    Flask Request

    Keys:
    attachment: Dict. Contains Attachment data
        databuffer: Dict. Contains the Buffer of the attachment data
            type: String. Contains what kind of Buffer it is.
            data: List[int]. A list of integers that represents a bytearray.
        mimetype: String. The format of the attachment.
        extension: String. The file extension of the attachment.
    scheduled_plan: Dict. Contains the data of the scheduled plan.
        title: String. The title of the dashboard that the schedule is made for.
        url: String. The url of the scheduled plan. This URL also contains the dashboard ID.
        scheduledPlanId: String. The ID of the scheduled plan.
        type: String. The type of scheduled plan.
    form_params: Dict. Contains the filled in form information.
        google_chat_webhook: String|None. The webhook URL of the google chat channel it is meant to send the summary to.
        slack_webhook: String|None. The webhook URL of the slack channel it is meant to send the summary to.

    Return
    String. "ok" | Response
    """
    try:
        message = flask.request.get_json()
        webhook = DashboardWebhook(**message)
        logger.log(f"Received webhook: {message}")

        # Retrieve Looker Data
        # Get Dashboard ID from the URL
        dashboard_id = get_dashboard_id_from_url(webhook.scheduled_plan.url)
        logger.log(f"Retrieved Dashboard ID: {dashboard_id}")

        # Once retrieved, request query data from Looker API
        looker = Looker()
        queries = looker.get_dashboard_queries(dashboard_id)
        logger.log(f"Retrieved queries: {queries}")

        # Build Prompts using queries
        # Read in query template from Bucket or Local files
        # Create prompts for each tile using the template
        if K_REVISION:
            prompt_bucket = CloudStorageBucket(PROJECT_ID, PROMPT_BUCKET)
            prompt_template = prompt_bucket.retrieve_file_as_string(f"prompts/{webhook.form_params.prompt_selection}.txt")
            logger.log(f"Retrieved Prompt template: {prompt_template}")
        else:
            with open("../prompts/main_prompt_template.txt", "r") as infile:
                prompt_template = infile.read()

        prompts = generate_prompts_from_queries(looker, queries, prompt_template)
        logger.log(f"Set prompts: {prompts}")

        # Summarise
        # Get Gemini to summarise the the query data
        vertex = VertexAi(PROJECT_ID, REGION)
        vertex.set_gemini_model("gemini-1.5-pro-001")

        summary_response_schema = SummaryResponseSchema().model_dump(serialize_as_any=True)
        summaries_json_format = vertex.generate_from_list_prompts(
            prompts, summary_response_schema
        )
        logger.log(f"Retrieved prompt results: {summaries_json_format}")

        # Log Vertex results in BigQuery for costs management
        # TODO: Implement this

        summaries_text_format = [
            convert_dict_to_text(
                json.loads(summary), ["title", "description", "summary", "next_steps"]
            )
            for summary in summaries_json_format
        ]
        logger.log(f"Converted summaries: {summaries_text_format}")
        # Upload PDF to Bucket and retrieve URL
        bucket = CloudStorageBucket(PROJECT_ID, PDF_BUCKET)
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        url = bucket.upload_file_from_string(
            bytes(bytearray(webhook.attachment.dataBuffer.data)),
            "application/pdf",
            f"{webhook.scheduled_plan.scheduledPlanId}/{timestamp}.pdf",
        )
        logger.log("Uploaded PDF")

        # Format prompts to be readable for each messaging platform
        # TODO: Implement this
        print(json.loads(summaries_json_format[0]))

        # Send messages to the specified channels
        if webhook.form_params.google_chat_webhook:
            google_chat = GoogleChat(webhook.form_params.google_chat_webhook)
            message = google_chat.create_message(summaries_text_format, url)
            logger.log(f"Created Google Chat message: {message}")
            google_chat.send_message(message)

        if webhook.form_params.slack_webhook:
            slack = Slack(webhook.form_params.slack_webhook)
            message = slack.create_message(summaries_text_format, url)
            logger.log(f"Created Slack message: {message}")
            slack.send_message(message)

        if webhook.form_params.teams_webhook:
            teams = Teams(webhook.form_params.teams_webhook)
            message = teams.create_message(summaries_text_format, url)
            logger.log(f"Created Slack message: {message}")
            teams.send_message(message)

        return flask.make_response(200)
    except Exception as e:
        return flask.abort(500)
    
@app.route("/prompts", methods=["GET"])
def retrieve_prompts():
    """
    Retrieve all prompts in GCS
    """

    # Check with GCS what prompts files are present and retrieve the names
    bucket = CloudStorageBucket(PROJECT_ID, PROMPT_BUCKET)

    prompt_names = bucket.check_bucket_contents()
    
    # Once the names are retrieved, send them back as a list in JSON body.
    return prompt_names
