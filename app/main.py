import logging
from flask import Flask
from openbrokerapi import api
import sys,os
from broker import MongoDBEnterpriseOSB
from flask import jsonify, render_template

logger = logging.getLogger('mdb-osb')
#fofo
log_level=os.environ.get("MDB_OSB_LOGLEVEL", "DEBUG")#"INFO")
logger.setLevel(log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

DEFAULT_USERNAME="test"
DEFAULT_PWD="test"

template_folder = os.environ.get('MDB_OSB_TEMPLATE_DIR','/mdb-osb-templates')
mdb_osb_config_path = "/"
app = Flask(__name__,template_folder=template_folder)

BROKER_PORT = os.getenv('MDB_OSB_PORT',80)
print(f'BROKER_PORT={BROKER_PORT}')

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
  logger.debug(f'Running in a Kubernetes cluster. KUBERNETES_SERVICE_HOST={k8s_host}')
  with open( "/mdb-osb/credentials/username", 'r') as secret:
    username = secret.read()
  with open( "/mdb-osb/credentials/password", 'r') as secret:
    password = secret.read()
else:
  logger.debug("Did not detect Kubernetes cluster")
  logger.debug(f'Running with default {DEFAULT_USERNAME}:{DEFAULT_PWD} credentials')
  username = DEFAULT_USERNAME
  password = DEFAULT_PWD

openbroker_bp = api.get_blueprint(MongoDBEnterpriseOSB(template_folder=template_folder,
                                                       logger=logger), 
                                  api.BrokerCredentials(username,password), logger)

app.register_blueprint(openbroker_bp)

import pprint
pprint.pprint(app)
if __name__ == "__main__":
    # Only for debugging while developing
    app.template_folder = '../templates'
    app.run(host="0.0.0.0", debug=True, port=BROKER_PORT)
