import os

import yaml
from flask import Flask, render_template

app = Flask(__name__)

_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.yaml")


@app.route("/")
def index():
    with open(_yaml_path) as f:
        site_data = yaml.safe_load(f)
    return render_template(
        "index.html",
        settings=site_data["settings"],
        links=site_data["social_links"],
        projects=site_data["projects"],
    )


if __name__ == "__main__":
    app.run(debug=True)
