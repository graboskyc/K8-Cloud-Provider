import json
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
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
        #self.k8.shell_deployment_script()
        """
        request["AppName"]
        request["UserRequestedAppName"]
        request["Attributes"]["App Name"]
        request["Attributes"]["App Tag"]
        request["Attributes"]["App Img"]
        request["Attributes"]["App Deploy Name"]
        request["Attributes"]["App Namespace"]
        request["Attributes"]["App Port"]
        request["Attributes"]["App Repl"]
        request["Attributes"]["App Name"]
        request["Attributes"]["App Type"]
        context.resource.attributes["Private Access Key"]
        """

        return "{'vm_name':'"+request["Attributes"]["App Name"]+"','vm_uuid':'55555','cloud_provider_resource_name':'test','auto_power_off':false,'wait_for_ip':false,'auto_delete':true,'autoload':true,'deployed_app_address':'127.0.0.1','public_ip':''}"
        pass

    def PowerOn(self, context, ports):
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Online", "Powered On")
        pass

    def PowerOff(self, context, ports):
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Online", "Powered On")
        pass

    def PowerCycle(self, context, ports, delay):
        PowerOff(context, ports)
        time.sleep(delay)
        PowerOn(context, ports)
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        pass

    def destroy_vm_only(self, context, ports):

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
