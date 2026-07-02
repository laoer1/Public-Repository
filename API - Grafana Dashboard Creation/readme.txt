# GRAFANA DASHBOARD AUTOMATION TOOLKIT

This toolkit does two things:

1. Batch-creates copies of a dashboard template for multiple sensors.
2. Uploads those dashboards directly to Grafana using the Grafana API.

---

## HOW IT WORKS

Step 1: generate_dashboards.py

* Reads your master JSON template file.
* Automatically creates a new JSON file for every sensor in your list.
* Finds and replaces the old sensor name with the new sensor name.
* Generates a unique ID (UID) for each dashboard so they don't overwrite each other.

Step 2: deploy_dashboards.py

* Takes a JSON dashboard file (or even a single panel/query).
* Fixes any missing layout properties automatically.
* Uploads the dashboard straight to your Grafana server.

---

## QUICKSTART GUIDE

1. Set your Grafana API token as an environment variable:
* Windows (CMD):  set GRAFANA_API_TOKEN="your_token_here"
* Windows (PS):   $env:GRAFANA_API_TOKEN="your_token_here"
* Mac/Linux:      export GRAFANA_API_TOKEN="your_token_here"


2. Open the scripts and update the configuration at the top:
* Change BASE_URL to your Grafana URL.
* Change INPUT_FILE_PATH to point to your files.


3. Run the scripts in order:
python generate_dashboards.py
python deploy_dashboards.py

---

## SETTINGS REFERENCE

* BASE_URL: Your Grafana server link (e.g., [https://your-grafana.com](https://www.google.com/search?q=https://your-grafana.com)).
* TARGET_FOLDER_ID: Where to put the dashboards. Set to None for the main folder.
* ALLOW_OVERWRITE: Set to True if you want to update/replace existing dashboards.