import json
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from K8S_App_Shell_OS import *
from DeployVMReturnObj import *
import uuid

class K8ShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.deployments = dict()
        self.deployments['Kubernetes Deploy Container From Image'] = self.deploy_img
        self.deployments['Kubernetes Deploy Container From File'] = self.deploy_file

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
        #self.k8 = K8S_APP_Shell_OS(context.resource.attributes["Service Account Username"], context.resource.attributes["Private Access Key"], context.resource.attributes["Public Access Key"])
        #self.k8.shell_health_check()
        pass

    def cleanup(self):
        pass

    def deploy_img(self, context, request, cancellation_context):
        
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
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "_" + uid
        attr = {'Password':lrra["Password"],"User":lrra["User"],"Public IP":lrra["Public IP"]}

        newAddr = context.resource.address + ":" + r["Attributes"]["App Port"]

        #appname, appns, appport, appimg, apptype, apprepl, appdepname, appdir
        #self.k8.shell_deployment_script()
        
        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], newAddr, "", attr)

        return ro
        pass

    def deploy_file(self, context, request, cancellation_context):
        
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
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "_" + uid
        attr = {'Password':lrra["Password"],"User":lrra["User"],"Public IP":lrra["Public IP"]}

        newAddr = context.resource.address + ":" + r["Attributes"]["App Port"]

        #appname, appns, appport, appimg, apptype, apprepl, appdepname, appdir
        #self.k8.shell_deployment_script()
        
        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], newAddr, "", attr)

        return ro
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
        return
        pass

    def destroy_vm_only(self, context, ports):
        #appname, appns
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
