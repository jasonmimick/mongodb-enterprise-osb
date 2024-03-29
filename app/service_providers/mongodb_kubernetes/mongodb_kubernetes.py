import abc
from typing import List
from werkzeug.exceptions import BadRequest
import os
from ..service_provider import MDBOSBServiceProvider
from .kubehelper import KubeHelper
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

class MongoDBKubernetesServiceProvider(MDBOSBServiceProvider):

  def __init__(self, broker):
    super().__init__(broker)
    self.my_services = {}
    self.provider_id = "mongodb-kubernetes"
    self.current_dir = os.path.dirname(os.path.abspath(__file__))
    self.mdb_template_folder = os.path.join(self.current_dir,'templates')
    self.site_template_folder = os.path.join(broker.template_folder,'mongodb-kubernetes')


                    
  def tags(self) -> List[str]:
    return [ "MongoDB Kubernetes Operator", "k8s", "containers", "docker" ] 


  def provision(self, instance_id: str, service_details: ProvisionDetails, async_allowed: bool) -> ProvisionedServiceSpec:
    self.logger.info("kubernetes provider - provision called") 
    self.logger.info("kubernetes provider - instance_id:%s" % instance_id) 
    self.logger.info("kubernetes provider - async_allowed:%s" % async_allowed) 
    self.logger.info("kubernetes provider  - service_details: %s" % vars(service_details))
    if not self.has_plan(service_details.plan_id):
      raise BadRequest(f'Invalid plan_id {service_details.plan_id}')      
    
    templates = self.load_templates(service_details.plan_id)    
    # merge parameters from 'context' and 'parameters' to templates
    parameters = { **service_details.parameters, **service_details.context }
    if not "name" in parameters.keys():
       self.logger.info("No 'name' detected. Injecting name based of instance_id=%s" % instance_id)
       parameters['name']=instance_id
    self.logger.info("render parameters: %s" % parameters)
    outputs = self.render_templates(templates,parameters)
    self.logger.debug( outputs )
    self.my_services[instance_id] = []
    if not 'name' in parameters.keys():
      self.logger.info("No 'name' parameter override found, default name from instance_id")
      parameters['name']=instance_id 
    for output in outputs.keys():
      self.logger.info("Provisioning: %s" % output) 
      KubeHelper.create_from_yaml( outputs[output]['rendered_template'], True) 
      self.my_services[instance_id].append( outputs[output]['rendered_template'] )
    # == 'hello-mongodb-kubernetes-operator':
    #  self.logger.info("provision hello-mongodb-kubernetes-operator start")
    n = parameters['name']
    spec = ProvisionedServiceSpec(
           dashboard_url="mongodb+srv://%s-svc/test?ssl=false" % n,
           operation="Provisioned MongoDB: %s" % n
    )
    return spec


  def deprovision(self, instance_id: str, service_details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
    self.logger.debug("---> deprovision")
    specs = self.my_services[instance_id]
    try:
      for output in specs:
        self.logger.info(f'DEprovisioning: {output}') 
        KubeHelper.delete_from_yaml( output['rendered_template'], True) 
    finally:
      # clean up
      deprovision_spec=DeprovisionServiceSpec(is_async=True)
      #del self.my_services[instance_id]
      return deprovision_spec
