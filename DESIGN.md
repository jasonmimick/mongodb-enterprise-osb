This document holds design notes/etc for collaboration.

mongodb-enterprise-osb implementation details


docker: simple lightwieght alpine python 3 
/mdb-osb-templates     - public folder for deployment templates
/mdb-osb   - default mount point for known config_maps and secrets
/mdb-osb/credentials    - admin user/pass for broker
/mdb-osb/configuration  - generic config map hols config parameters
app/main.py    - main flask 
app/broker     - all broker logic
app/service_providers/   - location of service providers
app/service_providers/private_cloud    - provider for operator, cloudmgr, etc services
app/service_providers/private_cloud/template  
                                       - template locations for mdb-owned templates
app/service_providers/mongodb_kubernetes - provider to cluster-admin manager db deployment templates


helm = install a bundle of manifests
kubeapps = big friendly buttons to install helm charts in a pretty ui
service catalog = connect your cluster to a cloud so you can use databases as a service again
open service broker = common spec for cloud providers so that they can all talk to service catalog

- OBS installer - 
https://svc-cat.io/docs/catalog-restrictions/


```
➜ curl -H 'X-Broker-Api-Version: 2.14' --user 'test:test' localhost:8080/v2/catalog
{
  "services": [
    {
      "bindable": true, 
      "description": "The MongoDB Enterprise Open Service Broker. Install, provision, bind, and manager MongoDB Enterprise Private Cloud deployments with ease.", 
      "id": "mongodb-open-service-broker", 
      "name": "mongodb-open-service-broker-service", 
      "plan_updateable": false, 
      "plans": [
        {
          "description": "Configures a local ConfigMap and Secret for MongoDB Cloud Manager to be user by the MongoDB Enterprise Kubernetes operator.", 
          "id": "mongodb-cloud-manager-config", 
          "name": "MongoDB Cloud Manager Configuration"
        }, 
        {
          "description": "Installs a demonstration version of the MongoDB Kubernetes Operator", 
          "id": "mongodb-kubernetes-operator", 
          "name": "MongoDB Enterprise Kubernetes Operator"
        }, 
        {
          "description": "Installs the companion MongoDB Atlas Open Service Broker.", 
          "id": "mongodb-atlas-osb", 
          "name": "MongoDB Atlas Open Service Broker"
        }
      ], 
      "tags": [
        "k8s", 
        "MongoDB", 
        "docker", 
        "Database", 
        "MongoDB Kubernetes Operator", 
        "containers"
      ]
    }
  ]
}
```


