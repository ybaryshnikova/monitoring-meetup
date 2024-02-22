# The snippet is taken from https://github.com/flipstone42/k8s-prometheus-custom-scaling.git
# to demonstrate how to use the prometheus_flask_exporter library to instrument a Flask application.
# The application is a simple web server that serves a single page with a button.
# When the button is clicked, the server increments a counter.
# The counter is exposed as a Prometheus metric.
# The application is instrumented with the GunicornInternalPrometheusMetrics class,
# which is a subclass of the PrometheusMetrics class.
# The GunicornInternalPrometheusMetrics class is designed to work with the Gunicorn web server.
# The application is a Flask application, so it uses the Flask class to create a new application instance.
# The application instance is then passed to the GunicornInternalPrometheusMetrics class to instrument the application.
# The @metrics.counter decorator is used to increment the counter.
# The first argument to the decorator is the name of the metric, and the second argument is the help text for the metric.
# The library is designed to work with the Gunicorn web server, but it can be used with other web servers as well.

from flask import Flask, render_template
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

application = Flask(__name__, static_folder="./public", template_folder="./templates")
metrics = GunicornInternalPrometheusMetrics(application)


@application.route("/")
def index():
    return render_template("index.html")


@application.route("/click-button", methods=["POST"])
@metrics.counter("demo_app_button_clicks", "Number of button presses by user")
def web_button():
    return {}
