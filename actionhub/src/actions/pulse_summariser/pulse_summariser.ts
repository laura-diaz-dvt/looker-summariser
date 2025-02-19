import * as Hub from "../../hub"
import axios from 'axios';
import { GoogleAuth } from 'google-auth-library';

const CLOUD_RUN_URL = 'https://cloud-run-summariser-536370090817.europe-west4.run.app'

export class SummariserAction extends Hub.Action {
    name = "pulse_summariser"
    label = "Pulse Summariser"
    iconName = "pulse_summariser/pulse_summariser.png"
    description = "Set a scheduler to send summaries"
    supportedActionTypes = [Hub.ActionType.Dashboard, Hub.ActionType.Query]
    params = [
        // {
        //     name: "email",
        //     label: "Email",
        //     required: true,
        //     sensitive: false,
        // }
    ]



    async execute(request: Hub.ActionRequest): Promise<Hub.ActionResponse> {
      const resp = new Hub.ActionResponse()
      const body = JSON.stringify(
        {
          scheduled_plan: request.scheduledPlan,
          form_params: request.formParams,
          attachment: request.attachment,
        }
      )
      const token = await this.getIdentityToken(CLOUD_RUN_URL)
      axios.post(CLOUD_RUN_URL , body, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      })
      .catch(function (error) {
        console.log(error)
        console.log('Error:', error.message);
      });
      return resp
    }

    async getIdentityToken(targetAudience: string): Promise<string> {
      const auth = new GoogleAuth();
      const client = await auth.getIdTokenClient(targetAudience);
      const token = await client.getRequestHeaders();
      return token['Authorization'].split(' ')[1]; // Extract token from `Authorization: Bearer <token>`
    }

    async retrievePrompts(token: string): Promise<Array<string>>{
      try {
        const resp = await axios.get(CLOUD_RUN_URL + "/prompts" , {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        })
        return resp.data
      } catch (error: any) {
        console.log(error)
        console.log('Error:', error.message);
        return []
      }
    }

    async form(request: Hub.ActionRequest) {
      console.log(request)
      const token = await this.getIdentityToken(CLOUD_RUN_URL)
      const prompts_array = await this.retrievePrompts(token)
      const prompts = prompts_array.map(str => ({
        name: str,
        label: str,
      }));


      const form = new Hub.ActionForm()
      form.fields = [
        {
          label: "Google Chat Webhook",
          name: "google_chat_webhook",
          type: "textarea",
        },
        {
          label: "Slack Webhook",
          name: "slack_webhook",
          type: "textarea",
        },
        {
          label: "Teams Webhook",
          name: "teams_webhook",
          type: "textarea",
        },
        {
          label: "Prompt",
          name: "prompt_selection",
          required: true,
          type: "select",
          options: prompts
        }
      ]
      return form
    }
}
  Hub.addAction(new SummariserAction())
