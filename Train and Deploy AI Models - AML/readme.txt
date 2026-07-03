# ReadMe
These two files help to train a model based on ML (Linear Regression, XGBoost and MLP).
This helps create prognose models for evaluation of deviation of sensor measurements (redundancy concept).
At the end a Trainned Model can be packaged and deployed to the ML Azure Services.

The script is meant to be used as a reference. Dependencies must be installed separately.

Kubernetes-Online-End Point - Goal is to:

1. Create a Container for the model
2. Deploy the Model (Obtain API)

This way, the deployment is more efficient for Azure (divide and conquer).

All proprietary source configurations, project identifiers, private endpoint domains, and active security credentials have been scrubbed or replaced with generic environment variable structures (os.getenv).

### Prerequisites
To run this template, make sure to set the following environment variables:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_ENDPOINT_API_KEY`