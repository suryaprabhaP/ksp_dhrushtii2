KSP_CrimeStatistics_5000:   sample request{
	"data": {
		"crime_subcategory": "ATM Gas Cutter Raid",
		"crime_year": 2024,
		"crime_category": "Organized Robbery",
		"crime_month": "September"
	}
}

response with exlanation on:
{
	"result": [
		55.09230422973633
	],
	"explanation": {
		"data": [
			[
				"crime_subcategory",
				0.042180589891970585,
				0.9998329464609416
			],
			[
				"crime_year",
				0.6666666666666666,
				-0.0003270968143582758
			],
			[
				"crime_category_1",
				0,
				0
			],
			[
				"crime_category_2",
				0,
				0.010135690456049047
			],
			[
				"crime_category_3",
				1,
				0
			],
			[
				"crime_category_4",
				0,
				0
			],
			[
				"crime_category_5",
				0,
				0
			],
			[
				"crime_category_6",
				0,
				0
			],
			[
				"crime_category_7",
				0,
				0
			],
			[
				"crime_category_8",
				0,
				0
			],
			[
				"crime_month",
				0.7915106955355637,
				-0.009641540102632355
			]
		],
		"baseValue": 54.09230422973633

KSP_Crimestatistics_5000 url: https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true

Headers: { 'X-QUICKML-ENDPOINT-KEY': 'a908dcf3cf420bd75fda737198d374259529cd975a40b9e219b959eb93e233aea4f87115161611cd6be123b22858d8e3', 'Authorization': 'Zoho-oauthtoken <access-token>', 'CATALYST-ORG': 60077159195, 'Environment': 'Development' }

sample request data:
{
	"data": {
		"crime_subcategory": "ATM Gas Cutter Raid",
		"crime_year": 2024,
		"crime_category": "Organized Robbery",
		"crime_month": "September"
	}
}

sample respnse data: {
	"result": [
		"<predicted-result>"
	],
	"explanation": "<model-explanation-json>"
}

OAuth Scope
QuickML.deployment.READ
HTTP Method
POST
Request Param Boolean Optional
explainModel 






KSP_Threat_AutoML_pipeline 
:
sample request:{
	"data": {
		"case_id": "KSP-GEO-00399",
		"incident_date": "2025-04-18",
		"crime_type": "Burglary",
		"latitude": 13.322197,
		"longitude": 74.715286,
		"nearest_city": "Udupi",
		"police_station": "Udupi Town PS",
		"case_status": "Under Investigation",
		"financial_loss_inr": 4233614
	}
}

sample response with explanation:
{
	"result": [
		"Critical"
	],
	"explanation": {
		"data": [
			[
				"incident_date",
				0.37219859233908575,
				0.47842509847985565
			],
			[
				"nearest_city_6",
				0,
				0.5215749015201443
			]
		],
		"baseValue": -1
	}
}
endpoint url: https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true


headers:
{ 'X-QUICKML-ENDPOINT-KEY': '27c18dcf8bef3f23b759afe09b45dc561752b6a71a290330cf990df34074bbd8e5db6bf813b9400704f9dd98e0e9646f', 'Authorization': 'Zoho-oauthtoken <access-token>', 'CATALYST-ORG': 60077159195, 'Environment': 'Development' }

OAuth Scope
QuickML.deployment.READ
HTTP Method
POST
Request Param Boolean Optional
explainModel 
request sample data:
{
	"data": {
		"case_id": "KSP-GEO-00399",
		"incident_date": "2025-04-18",
		"crime_type": "Burglary",
		"latitude": 13.322197,
		"longitude": 74.715286,
		"nearest_city": "Udupi",
		"police_station": "Udupi Town PS",
		"case_status": "Under Investigation",
		"financial_loss_inr": 4233614
	}
}
sample data response:
{
	"result": [
		"<predicted-result>"
	],
	"likelihood_score": [
		0.98
	],
	"explanation": "<model-explanation-json>"
}

KSP_Geospatial_DBSCAN_Pipeline:

endpoints:https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict


sample data request:
{
	"data": {
		"latitude": 12.981073,
		"longitude": 77.740961,
		"severity_weight": 51
	}
}

same data result:
{
	"result": [
		"<predicted-result>"
	]
}

headers:

{ 'X-QUICKML-ENDPOINT-KEY': '0742765af06e9105d37e37aaf7c40df3f501611b15735dceb35a16994c1be2dde60c4c342faf4212c5fe4087991c9b8c', 'Authorization': 'Zoho-oauthtoken <access-token>', 'CATALYST-ORG': 60077159195, 'Environment': 'Development' }

OAuth Scope
QuickML.deployment.READ
HTTP Method
POST



