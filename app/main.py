import logging
from flask import Flask
from openbrokerapi import api
import os
from broker import MongoDBEnterpriseOSB

logger = logging.getLogger(__name__)

from flask import jsonify, render_template

template_folder = os.environ.get('MDB_OSB_TEMPLATE_DIR','/mdb-osb-templates')
app = Flask(__name__,template_folder=template_folder)


@app.route("/signup")
def signup():
  return render_template('signup.html')

@app.route("/")
def hello():
    return "Hello World from Flask in a uWSGI Nginx Docker container with \
     Python 3.7 (from the example template)"

# If we're running inside a kubernetes cluster, then we expect the credentials for
# the broker to be in a file mounted from a secret.
if os.environ.get('KUBERNETES_SERVICE_HOST'):
  k8s_host = os.environ.get('KUBERNETES_SERVICE_HOST')
  print("Detected running in a Kubernetes cluster. KUBERNETES_SERVICE_HOST=%s" % k8s_host)
  config_path = "/broker/broker-config"
  with open( ("%s/username" % config_path), 'r') as secret:
    username = secret.read()
  with open( ("%s/password" % config_path), 'r') as secret:
    password = secret.read()
else:
  print("Did not detect Kubernetes cluster. Running with default 'test/test' credentials")
  username = "test"
  password = "test"

openbroker_bp = api.get_blueprint(MongoDBEnterpriseOSB(template_folder=template_folder), 
                                  api.BrokerCredentials(username,password), logger)

app.register_blueprint(openbroker_bp)

import pprint
pprint.pprint(app)
if __name__ == "__main__":
    # Only for debugging while developing
    app.template_folder = '../templates'
    app.run(host="0.0.0.0", debug=True, port=8080)
