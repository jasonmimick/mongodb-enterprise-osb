import abc
from typing import List
from werkzeug.exceptions import BadRequest
import os
from ..service_provider import MDBOSBServiceProvider
#from .kubehelper import KubeHelper
from ..mongodb_kubernetes.mongodb_kubernetes import MongoDBKubernetesServiceProvider
from openbrokerapi.catalog import (
    ServicePlan,
)
from openbrokerapi.service_broker import (
    BindDetails,
    BindState,
    ProvisionedServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionDetails,
    ProvisionDetails,
    ProvisionState,
    UnbindDetails,
    UpdateDetails,
    ServiceBroker,
    DeprovisionServiceSpec,
    DeprovisionDetails)
from kubernetes import client, config, utils
import yaml

class MongoDBEnterpriseToolsServiceProvider(MDBOSBServiceProvider):

  def __init__(self, broker):
    super().__init__(broker)
    self.my_services = {}
    self.provider_id = "mongodb-enterprise-tools"
    self.current_dir = os.path.dirname(os.path.abspath(__file__))
    self.mdb_template_folder = os.path.join(self.current_dir,'templates')
    self.site_template_folder = os.path.join(broker.template_folder,'mongodb-entperise-tools')


                    
  def tags(self) -> List[str]:
    return [ "MongoDB Enterprise Tools", "BI Connector", "SQL Connector", "charts", "mongo apps" ] 


  def provision(self, instance_id: str, service_details: ProvisionDetails, async_allowed: bool) -> ProvisionedServiceSpec:
    self.logger.warn("enterprise-tools provider - provision called - NOT IMPLEMENTED")
		# TODO - delgate kube stuff to the MongoDBKubernetesServiceProvider or KubeHelper
    raise BadRequest(f'Sorry, we\'re not quite ready for business just yet, stay tuned... #mdbosb')      
    


  def deprovision(self, instance_id: str, service_details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
    self.logger.warn("enterprise-tools provider - deprovision called - NOT IMPLEMENTED")
		# TODO - delgate kube stuff to the MongoDBKubernetesServiceProvider or KubeHelper
    raise BadRequest(f'Sorry, we\'re not quite ready for business just yet, stay tuned... #mdbosb')      
