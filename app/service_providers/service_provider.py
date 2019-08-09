import abc
import os,sys
from typing import List
import glob 
import urllib
from jinja2 import Template
from openbrokerapi.service_broker import (
    BindDetails,
    BindState,
    ProvisionedServiceSpec,
    DeprovisionServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionDetails,
    ProvisionDetails,
    ProvisionState,
    UnbindDetails,
    UpdateDetails,
    ServiceBroker)
import yaml

from openbrokerapi.catalog import (
    ServicePlan,
)

#from broker import HTTPException

# interface for services
class MDBOSBServiceProvider(object, metaclass=abc.ABCMeta):
  
  def __init__(self, broker):
    self.broker = broker
    self.logger = broker.logger
    self.__plan_ids = self.plan_ids()
    self.myplans = self.__load_plans() 

  def plan_ids(self):
    caller = sys._getframe(2).f_globals['__file__'].split('.')[0]
    self.logger.debug(f'caller={caller}')
    callers_path = os.path.dirname(caller)
    self.logger.debug(f'callers_path={callers_path}')
    self.current_dir = callers_path
    templates_dir = os.path.join(callers_path,'templates')
    self.logger.debug(f'templates_dir={templates_dir}')
    plans_dir = os.environ.get('MDB_OSB_TEMPLATE',templates_dir)
    self.logger.info(f'plan_dirs={plans_dir}')
    plan_ids = os.listdir(plans_dir)
    self.plans_dir = plans_dir
    self.logger.info(f'plan_ids={plan_ids}')
    return plan_ids

  def load_templates(self,plan_id):
    # Load all templates in repo
    template_dir = "/broker/templates/{0}/{1}/".format(self.provider_id,plan_id)
    self.logger.info("load_templates template_dir=%s" % template_dir)
    template_filename_wildcard = "*.yaml"
    template_files = glob.glob("%s/%s" % (template_dir, template_filename_wildcard))
    templates = {}
    self.logger.info("load_templates: %s" % template_files)
    for template_file in template_files:
      self.logger.info("loading: %s" % template_file)
      with open(template_file, 'r') as t:
        template = t.read()
        self.logger.debug("loaded template: %s" % template)
        templates[template_file] = { 'template' : str(template), 'rendered_template' : None }

    template_filename_wildcard = "*.url"
    template_files = glob.glob("%s/%s" % (template_dir, template_filename_wildcard))
    self.logger.info("load_templates: %s" % template_files)
    for template_file in template_files:
      self.logger.info("loading: %s" % template_file)

      with open(template_file, 'r') as t:
        url = t.read()
        self.logger.info("loading template from url: %s" % url)
        with urllib.request.urlopen(url) as u:
          template = u.read()
          self.logger.debug("loaded template: %s" % template)
          templates[template_file] = { 'template' : str(template), 'rendered_template' : None }
    return templates

  def render_templates(self, templates, parameters):
    rendered_templates = {}
    self.logger.info("render_templates: %s" % templates.keys())
    for template_name in templates.keys():
      
      template = templates[template_name]
      #self.logger.info('template:%s' % template)
      rendered_templates[template_name] = {}
      rendered_templates[template_name]['template'] = template['template']
      #if "{{ " in template['template']:
      t = Template( template['template'] )
      rendered_template = t.render(parameters)
      #else:
      #  self.logger.info("No parameters detected in template.")
      #  rendered_template = template['template']
      rendered_templates[template_name]['rendered_template'] = rendered_template
      self.logger.info('rendered_template:%s' % rendered_template)
    return rendered_templates


  def has_plan(self,plan_id) -> bool:
    return [p for p in self.myplans if p.id == plan_id]


  def plans(self) -> List[ServicePlan]:
    self.logger.debug(f'plans - service provider {self.myplans}')
    return self.myplans

  def __load_plans(self) -> List[ServicePlan]:
    plans = []
      #if not os.path.exists(plan_file):
        #self.logger.warn(f'No "plan.yaml" found in {self.plans_dir}, unable to load additional plan information. This may be just fine, maybe this plan does not need one. Consider adding an empty .plan.yaml.ignore file in the repoted path to suppress this warning.') 
      #  self.logger.warn(f'No "plan.yaml" found in {self.plans_dir}.') 
      #plan_info = yaml.load(plan_file)

    plan_ids = self.__plan_ids
    for plan_id in plan_ids:
      this_plan_dir = os.path.join(self.plans_dir, plan_id )
      #plan_file = os.path.join( this_plan_dir, 'plan.yaml' )
      #ignore_plan_file = os.path.join( self.plans_dir, '.plan.yaml.ignore')
      #if not os.path.exists( ignore_plan_file ):
      #  plan = plan_from_plan_file(plan_file) 
      #else:
      desc = f'Plan id:{plan_id} plan_dir:{this_plan_dir}'
      plan = ServicePlan( id=plan_id,
                          name=plan_id,
                          description=desc)
      #
      plans.append( plan )
    self.logger.debug(f'__load_plans {plans}')
    return plans

  @abc.abstractmethod
  def tags(self) -> List[str]:
    pass  

  @abc.abstractmethod
  def provision(self, instance_id: str, service_details: ProvisionDetails, async_allowed: bool) -> ProvisionedServiceSpec:
    pass

  @abc.abstractmethod
  def deprovision(self, instance_id: str, service_details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
    pass

