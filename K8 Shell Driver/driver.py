import json
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
from K8S_App_Shell_OS import *
import pickle

class K8ShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.deployments = dict()
        self.deployments['Deploy Container'] = self.deploy_vm

        #self.k8 = K8S_APP_Shell_OS(self.k8appdata)
        #self.k8.shell_health_check()
        pass

    def Deploy(self, context, request=None, cancellation_context=None):
        app_request = json.loads(request)
        deployment_name = app_request['DeploymentServiceName']
        if deployment_name in self.deployments.keys():
            deploy_method = self.deployments[deployment_name]
            return deploy_method(context,request,cancellation_context)
        else:
            raise Exception('Could not find the deployment')

    def initialize(self, context):
        pass

    def cleanup(self):
        pass

    def deploy_vm(self, context, request, cancellation_context):
        ## REMOVE THIS BLOCK AS IT IS NOT OFFICIAL LOGGING!
        with open("C:/temp/k8shelltestlog_deploy.txt", 'w+') as fh:
            fh.write(pickle.dumps(context))
            fh.write(pickle.dumps(request))

        #self.k8.shell_deployment_script()

        return "{'vm_name':'Test123','vm_uuid':'55555','cloud_provider_resource_name':'test','auto_power_off':false,'wait_for_ip':false,'auto_delete':true,'autoload':true,'deployed_app_address':'127.0.0.1','public_ip':''}"
        pass

    def PowerOn(self, context, ports):
        pass

    def PowerOff(self, context, ports):
        pass

    def PowerCycle(self, context, ports, delay):
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        pass

    def destroy_vm_only(self, context, ports):
        ## REMOVE THIS BLOCK AS IT IS NOT OFFICIAL LOGGING!
        with open("C:/temp/k8shelltestlog_destroy.txt", 'w+') as fh:
            fh.write(pickle.dumps(context))
            fh.write(pickle.dumps(ports))

        #self.k8.shell_teardown_script()
        pass

    def GetApplicationPorts(self, context, ports):
        pass

    def get_inventory(self, context):
        return AutoLoadDetails([], [])
        pass

    def GetAccessKey(self, context, ports):
        pass

    def GetVmDetails(self, context, cancellation_context, requests):
        pass
