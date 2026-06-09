import newrelic.agent
import os
from flask import Flask, request
import requests
import logging
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldclient.hook import Hook, Metadata
import ldobserve
from ldobserve import ObservabilityConfig, ObservabilityPlugin

app = Flask(__name__)
logger = logging.getLogger(__name__)
key = os.environ["DARKLY_SDK_KEY"]

class NewRelicHook(Hook):
    @property
    def metadata(self) -> Metadata:
        return Metadata(name="newrelic-hook")

    def before_evaluation(self, series_context, data):
        return data

    def after_evaluation(self, series_context, data, detail):
        try:
            logger.info("Attaching data to NR span")
            attrs = {
              'feature_flag.key': series_context.key,
              'feature_flag.provider.name': 'LaunchDarkly',
              'feature_flag.context.id': series_context.context.key,
            }
            if isinstance(detail.variation_index, int):
                attrs['feature_flag.result.variationIndex'] = detail.variation_index
            if hasattr(detail, "reason") and detail.reason.get("kind"):
                attrs['feature_flag.result.reason.kind'] = detail.reason["kind"]
            if hasattr(detail, "reason") and detail.reason.get("in_experiment"):
                attrs['feature_flag.result.reason.inExperiment'] = True
            if getattr(detail, "value", None):
                attrs['feature_flag.result.value'] = detail.value
            trace = newrelic.agent.current_trace()
            if not trace:
                raise Exception("No active trace. Unable to attach Darkly data to span.")
            for key, value in attrs.items():
                trace.add_custom_attribute(key, value)
        except Exception as e:
            logger.error("[newrelic-hook] failed to enrich span", exc_info=True)
        return data

observability_config = ObservabilityConfig(
  service_name="hstepanek-proto",
  service_version="0.0.0",
)
plugin = ObservabilityPlugin(observability_config) #, auto_instrumentation=False)
example_hook = NewRelicHook()
ldclient.set_config(Config(key, hooks=[example_hook], plugins = [plugin]))

if not ldclient.get().is_initialized():
    print('SDK failed to initialize')
    exit()

# For onboarding purposes only we flush events as soon as
# possible so we quickly detect your connection.
# You don't have to do this in practice because events are automatically flushed.
ldclient.get().flush()
print('SDK successfully initialized')


@app.route("/")
def hello_world():
    logger.warning("This is a warning inside / endpoint")
    context = Context.builder("send-request") \
        .set("firstName", "Sandy") \
        .set("lastName", "Smith") \
        .set("email", "sandy@example.com") \
        .set("groups", ["Acme", "Global Health Services"]) \
        .build()
    flag_value = ldclient.get().variation("send-request", context, False)
    if flag_value:
        requests.get("http://example.com")
        logger.warning("Sent request, feature flag is enabled.")
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)
