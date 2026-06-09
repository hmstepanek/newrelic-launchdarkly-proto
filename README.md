# newrelic-launchdarkly-proto
Prototype of New Relic Launch Darkly Integration

This prototype creates a custom New Relic hook in Launch Darkly's SDK to add feature data to the current New Relic span/trace.

At the end of a New Relic transaction, when the agent is preparing span data to add to its harvest queue, before sampling is applied, all span data is added to the Launch Darkly SDK client queue. 

## Installation instructions:
1. Clone the github repo.
1. Create a Python virtual env: `virtualenv -p python pyVirtual`. (Python >= 3.10 is required.)
1. Activate the virtual env: `. py312/bin/activate`.
1. Install dependencies: `pip install -r requirements.txt`
1. Generate a [New Relic license key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#ingest-license-key). Generate a [Launch Darkly SDK key](https://launchdarkly.com/docs/home/account/environment/keys). Set environment variables:
   ```
   export NEW_RELIC_LICENSE_KEY=<new relic license key> 
   export DARKLY_SDK_KEY=<launch darkly sdk key> 
   export NEW_RELIC_CONFIG_FILE=newrelic.ini
   ```
1. Run the application: `newrelic-admin run-program python app.py`
