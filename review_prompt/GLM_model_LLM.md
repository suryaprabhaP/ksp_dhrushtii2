endpoint url of the model https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/glm/chat and OAuth Scope
QuickML.deployment.READ
Authentication
OAuth
HTTP Method POST.  headers: { "CATALYST-ORG": "60077159195", "Authorization": "Zoho-oauthtoken <access-token>" }.   integeration implementation features: //using request
import requests
		
url = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/glm/chat"
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer YOUR_TOKEN", 
	"CATALYST-ORG": "60077159195"
}
data = {
	"model": "crm-di-glm47b_30b_it",
	"messages": [
		{
			"role": "system",
			"content": "You are a helpful assistant."
		},
		{
			"role": "user",
			"content": "What's the weather like in Paris today?"
		}
	],
	"max_tokens": 500,
	"temperature": 0.7,
	"stream": false,
	"chat_template_kwargs": {
		"enable_thinking": true
	},
	"tools": [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get current weather information for a specific location",
				"parameters": {
					"type": "object",
					"properties": {
						"location": {
							"type": "string",
							"description": "The city and country, e.g. Paris, France"
						},
						"unit": {
							"type": "string",
							"enum": [
								"celsius",
								"fahrenheit"
							],
							"description": "Temperature unit"
						}
					},
					"required": [
						"location"
					]
				}
			}
		}
	],
	"tool_choice": "auto"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())


//using fetch
const url = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/glm/chat";
const headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer YOUR_TOKEN", 
	"CATALYST-ORG": "60077159195"
};
const data = {
	"model": "crm-di-glm47b_30b_it",
	"messages": [
		{
			"role": "system",
			"content": "You are a helpful assistant."
		},
		{
			"role": "user",
			"content": "What's the weather like in Paris today?"
		}
	],
	"max_tokens": 500,
	"temperature": 0.7,
	"stream": false,
	"chat_template_kwargs": {
		"enable_thinking": true
	},
	"tools": [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get current weather information for a specific location",
				"parameters": {
					"type": "object",
					"properties": {
						"location": {
							"type": "string",
							"description": "The city and country, e.g. Paris, France"
						},
						"unit": {
							"type": "string",
							"enum": [
								"celsius",
								"fahrenheit"
							],
							"description": "Temperature unit"
						}
					},
					"required": [
						"location"
					]
				}
			}
		}
	],
	"tool_choice": "auto"
};

fetch(url, {
	method: "POST",
	headers: headers,
	body: JSON.stringify(data),
})
	.then(response => response.json())
	.then(data => console.log(data))
	.catch(error => console.error("Error:", error)); this i in java script and we only have javascript and java for this and this is sample request:{
	"model": "crm-di-glm47b_30b_it",
	"messages": [
		{
			"role": "system",
			"content": "You are a helpful assistant."
		},
		{
			"role": "user",
			"content": "What's the weather like in Paris today?"
		}
	],
	"max_tokens": 500,
	"temperature": 0.7,
	"stream": false,
	"chat_template_kwargs": {
		"enable_thinking": true
	},
	"tools": [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get current weather information for a specific location",
				"parameters": {
					"type": "object",
					"properties": {
						"location": {
							"type": "string",
							"description": "The city and country, e.g. Paris, France"
						},
						"unit": {
							"type": "string",
							"enum": [
								"celsius",
								"fahrenheit"
							],
							"description": "Temperature unit"
						}
					},
					"required": [
						"location"
					]
				}
			}
		}
	],
	"tool_choice": "auto"
} and sample response:{
	"id": "chatcmpl-a63f3e90fc53147d125f6084478fa794",
	"object": "chat.completion",
	"created": 1775021675,
	"model": "crm-di-glm47b_30b_it",
	"choices": [
		{
			"index": 0,
			"message": {
				"role": "assistant",
				"content": "I'll check the current weather in Paris for you.",
				"refusal": null,
				"annotations": null,
				"audio": null,
				"function_call": null,
				"tool_calls": [
					{
						"id": "chatcmpl-tool-b98ab1399e7f3770",
						"type": "function",
						"function": {
							"name": "get_weather",
							"arguments": "{\"location\": \"Paris, France\"}"
						}
					}
				],
				"reasoning": "The user is asking for the weather in Paris today. I have access to a get_weather function that can provide current weather information. Let me check the parameters:\n\n- location: required - \"Paris, France\" (since they just said \"Paris\" and it's commonly understood to be Paris, France)\n- unit: optional - not specified by the user, so I won't include it since the instructions say not to make up values for optional parameters\n\nI should call the function with \"Paris, France\" as the location."
			},
			"logprobs": null,
			"finish_reason": "tool_calls",
			"stop_reason": 154829,
			"token_ids": null
		}
	],
	"usage": {
		"prompt_tokens": 219,
		"total_tokens": 350,
		"completion_tokens": 131,
		"prompt_tokens_details": null
	},
	"prompt_logprobs": null
} and possible error response: BAD REQUEST(400)
INTERNAL SERVER ERROR(500) and sample error response {
	"code": "INTERNAL SERVER ERROR",
	"message": "Error occurred in LLM Agent",
	"details": {
		"reason": ""
	}
} and Input Token Limitations
Upto 200k tokens.  Parameters
30B total, 3B active (MoE) and Model Size
30 Billion parameters
Training Size
Not publicly disclosed. Additional Capabilities
Strong Coding Ability
Multi-step Reasoning Stability
Tool & Agent Support
Conversational Chat Completion. 


