import logging
from flask import Flask
from http import HTTPStatus
from openbrokerapi import api
from openbrokerapi.catalog import (
    ServicePlan,
)
from openbrokerapi.log_util import basic_config
from openbrokerapi.helper import to_json_response
from openbrokerapi import api
from openbrokerapi import errors
from openbrokerapi.service_broker import (
    ServiceBroker,
    UnbindDetails,
    BindDetails,
    Binding,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    UpdateDetails,
    UpdateServiceSpec,
    ProvisionDetails,
    ProvisionedServiceSpec,
    Service,
    LastOperation)
from openbrokerapi.response import (
    BindResponse,
    CatalogResponse,
    DeprovisionResponse,
    EmptyResponse,
    ErrorResponse,
    LastOperationResponse,
    ProvisioningResponse,
    UpdateResponse,
)

import os
from service_providers import service_provider
from service_providers.private_cloud import private_cloud
from service_providers.mongodb_kubernetes import mongodb_kubernetes
from service_providers.mongodb_enterprise_tools import mongodb_enterprise_tools


from flask import jsonify

class HTTPException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class MongoDBEnterpriseOSB(ServiceBroker):

    def __init__(self,template_folder='',logger=logging.getLogger(__name__)):
      self.logger = logger
      self.service_providers = {}
      self.template_folder = template_folder
      self.provisioned_services = {}
      self.service_plans = {}
      self.__last_op = {}
      self.__catalog = {}

      # Private Cloud Provider
      pc = private_cloud.PrivateCloudServiceProvider(self)
      self.service_providers['private-cloud'] = pc
    
      # Standard MongoDB Templates
      mk = mongodb_kubernetes.MongoDBKubernetesServiceProvider(self)
      self.service_providers['mongodb-kubernetes'] = mk

      # Enterprise Tools
      ets = mongodb_enterprise_tools.MongoDBEnterpriseToolsServiceProvider(self)
      self.service_providers['mongodb-enterprise-tools'] = ets

      # Private Providers
      # Here, we will load the customer/cluster specific private providers.
  
    def catalog(self) -> Service:
      
      self.logger.debug("loaded service providers\n".join("{}\t{}".format(k, v) for k, v in self.service_providers.items()))
      plans = []
      tags = ['MongoDB', 'Database' ]
      for provider_name in self.service_providers.keys():
        self.logger.debug("loading plans for provider: %s" % provider_name)
        provider = self.service_providers[provider_name]
        self.logger.debug(f'{provider}')
        provider_plans = provider.plans()
        for plan in provider_plans:
          self.logger.debug(f'plan={plan}')
          self.service_plans[plan.id]= { 'provider_name' : provider_name, 'plans' : provider_plans }
        plans.extend( provider_plans )
        tags.extend( provider.tags() )
            
      # Omitting this, needs nested v2.DashboardClient type
      #     dashboard_client='http://mongodb-open-service-broker:8080',

      catalog = Service(
            id='mongodb-open-service-broker',
            name='mongodb-open-service-broker-service',
            description='The MongoDB Enterprise Open Service Broker. https://mongodb.com/osb',
            bindable=True,
            plans=plans,
            tags=list(set(tags)),
            plan_updateable=False,
      )
      self.__last_op = LastOperation("catalog", catalog )
      self.__catalog = catalog
      return catalog

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        self.logger.info("provision") 
        provider_name = self.service_plans[service_details.plan_id]['provider_name']
        provider = self.service_providers[provider_name]
        self.logger.info("provider_name=%s, provider=%s" % ( provider_name, provider) )
        self.provisioned_services[instance_id]={ "provider" : provider,
"plan_id" : service_details.plan_id, "spec" : None, "last_op" : LastOperation("provision","Started") } 
        self.logger.info("request to provision plan_id=%s" % service_details.plan_id)
        spec = provider.provision(instance_id, service_details, async_allowed)
        self.provisioned_services[instance_id]={ "provider" : provider, "plan_id" : service_details.plan_id, "spec" : spec, "last_op" : LastOperation("provision",spec) }
        return spec

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        self.logger.info("bind") 

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        self.logger.info("update") 

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        self.logger.info("deprounbind") 

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
        self.logger.info("deprovision") 
        self.logger.info("request to deprovision instance_id=%s" % instance_id)
        self.logger.info("deprovision: details=%s" % details)
        if not instance_id in self.provisioned_services.keys():
          raise errors.ErrInstanceDoesNotExist()
        provider = self.provisioned_services[instance_id]["provider"]
        result = provider.deprovision(instance_id, details, async_allowed)
        self.provisioned_services[instance_id]["spec"] = result
        self.provisioned_services[instance_id]["last_op"]="deprovision"
        return result

    def check_plan_id(self, plan_id: str) -> bool:
        return ( plan_id in self.service_plans.keys() )


    def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
        self.logger.info("last_opertation") 
        if not instance_id in self.provisioned_services:
          raise errors.ErrInstanceDoesNotExist()
        spec = self.provisioned_services[instance_id]["spec"]
        op = self.provisioned_services[instance_id]["last_op"]
        lo = LastOperation(op, spec)
        return lo

