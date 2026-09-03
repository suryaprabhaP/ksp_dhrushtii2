i also have another model, VL-Qwen3.6-35B-A3B  integeration implement feature: //using request
import requests
		
url = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/vlm/chat"
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer YOUR_TOKEN", 
	"CATALYST-ORG": "60077159195"
}
data = {
	"prompt": "Fields to extract: Contact details, Skills, education and project details and give the results in the json format with keys as the above fields to extract and values as the original value in the document image",
	"model": "VL-Qwen3.6-35B-A3B",
	"images": [
		"<base64-encoded-image-1>",
		"<base64-encoded-image-2>"
	],
	"system_prompt": "Be concise and factual.",
	"top_k": 50,
	"top_p": 0.9,
	"temperature": 0.7,
	"max_tokens": 500
}

response = requests.post(url, json=data, headers=headers)
print(response.json())


//using fetch
const url = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/vlm/chat";
const headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer YOUR_TOKEN", 
	"CATALYST-ORG": "60077159195"
};
const data = {
	"prompt": "Fields to extract: Contact details, Skills, education and project details and give the results in the json format with keys as the above fields to extract and values as the original value in the document image",
	"model": "VL-Qwen3.6-35B-A3B",
	"images": [
		"<base64-encoded-image-1>",
		"<base64-encoded-image-2>"
	],
	"system_prompt": "Be concise and factual.",
	"top_k": 50,
	"top_p": 0.9,
	"temperature": 0.7,
	"max_tokens": 500
};

fetch(url, {
	method: "POST",
	headers: headers,
	body: JSON.stringify(data),
})
	.then(response => response.json())
	.then(data => console.log(data))
	.catch(error => console.error("Error:", error)); . this is in javascript.  enpoint url: https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/vlm/chat .  headers:  { "CATALYST-ORG": "60077159195", "Authorization": "Zoho-oauthtoken <access-token>" }  ,  OAuth Scope
QuickML.deployment.READ
Authentication
OAuth
HTTP Method
POST. LLM Details
Model Size
35 Billion parameters
Visual Encoder
Newly-structured vision transformer with 2D-RoPE and window attention for native resolution processing
Parameters
35 Billion parameters with Active 3 Billion parameter
Input Token Limitations
Supports up to three images (6k tokens total) plus text (3k tokens), for approximately 9k tokens overall.
Additional Capabilities
Multimodal Reasoning
Multilingual Visual Text Recognition (OCR)
Document & Chart Question Answering
Structured Output (JSON, bounding boxes, points).  this is sample request: {
	"prompt": "Fields to extract: Contact details, Skills, education and project details and give the results in the json format with keys as the above fields to extract and values as the original value in the document image",
	"model": "VL-Qwen3.6-35B-A3B",
	"images": [
		"<base64-encoded-image-1>",
		"<base64-encoded-image-2>"
	],
	"system_prompt": "Be concise and factual.",
	"top_k": 50,
	"top_p": 0.9,
	"temperature": 0.7,
	"max_tokens": 500
}  sample response: {
	"request_id": "a9df919e72da4ef1a1a9360fdb025641",
	"model": "VL-Qwen3.6-35B-A3B",
	"response": "```json\n{\n  \"Contact\": {\n    \"Email\": \"person.one@email.com\",\n    \"Phone\": \"+91 98 7654 3210\",\n    \"Address\": \"H#1, Area - Chennai 600001\"\n  },\n  \"Skills\": [\n    \"Windows\",\n    \"HTML5\",\n    \"UI/UX DESIGN\",\n    \"Communication\",\n    \"MS Office\",\n    \"CSS3\",\n    \"WordPress\",\n    \"Teamwork\",\n    \"Internet\",\n    \"JAVASCRIPT\",\n    \"Python\",\n    \"Project Mgmt.\"\n  ],\n  \"Education\": {\n    \"Degree\": \"Bachelor of Engineering in Computer Science\",\n    \"Institute\": \"National Institute of Technology, Chennai\",\n    \"Year\": \"Aug, 2023\"\n  },\n  \"Projects\": [\n    \"Built a responsive e-commerce website for a local startup, resulting in a 15% increase in online sales.\",\n    \"Contributed bug fixes and feature enhancements to the Bootstrap CSS framework.\",\n    \"Personal portfolio website showcasing coding skills and past projects.\",\n    \"Volunteered for Hack for Education, creating an e-learning platform for underprivileged children.\"\n  ]\n}\n```",
	"metrics": {
		"input_text_token_length": 57,
		"input_image_token_length": 1750,
		"input_guided_prompt_length": 0,
		"output_text_token_length": 256,
		"queue_wait_time": 2.4174728393554688,
		"processing_time": 6.480634450912476,
		"total_time_taken": 8.898107290267944
	}
} and possible error response: BAD REQUEST(400)
INTERNAL SERVER ERROR(500) .  sample error response: {
	"code": "INTERNAL SERVER ERROR",
	"message": "Error occurred in LLM Agent",
	"details": {
		"reason": ""
	}
}. Additional Capabilities
Multimodal Reasoning
Multilingual Visual Text Recognition (OCR)
Document & Chart Question Answering
Structured Output (JSON, bounding boxes, points).