import jsonpickle
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from K8S_App_Shell_OS import *
import os, sys
import json

class K8ShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """

        # from a json file...
        self.k8appdata = dict()
        self.k8appdata["AppDir1"] = "./node-demo-app-master"
        self.k8appdata["AppName1"] = "demo-app"
        self.k8appdata["AppType1"] = "node"
        self.k8appdata["AppImgID1"] = "22e36adaa33c"
        self.k8appdata["AppImgURL1"] = "index.docker.io/in4it/node-demo-app"
        self.k8appdata["Appyaml1"] = "demo.app.yml"
        self.k8appdata["AppName2"] = "busybox"
        self.k8appdata["AppURI3"] = "https://k8s.io/docs/tasks/run-application/deployment.yaml"
        self.k8appdata["AppName4"] = "nginx"
        self.k8appdata["AppImg4"] = "nginx:1.9.1"
        self.k8appdata["AppDeployName4"] = "nginx-deployment"
        self.k8appdata["AppPort4"] = "80"
        self.k8appdata["AppRepl4"] = "3"
        self.k8appdata["AppNamespace4"] = "dev-test"
        self.k8appdata["AppType4"] = "app"


        self.deployments = dict()
        self.deployments['Deploy Container'] = self.deploy_vm

        self.k8 = K8S_APP_Shell_OS(k8appdata)
        self.k8.shell_health_check()

    def Deploy(self, context, request=None, cancellation_context=None):
        app_request = jsonpickle.decode(request)
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
        fh = os.open("C:/temp/k8shelltestlog.txt",os.O_RDWR|os.CREAT)
        os.write(fh,json.dumps(context))
        os.write(fh,json.dumps(ports))
        #self.k8.shell_teardown_script()
        pass

    def PrepareConnectivity(self, context, request, cancellation_context):
        pass

    def CleanupConnectivity(self, context, request):
        pass

    def GetApplicationPorts(self, context, ports):
        pass

    def get_inventory(self, context):
        pass

    def GetAccessKey(self, context, ports):
        pass

    def GetVmDetails(self, context, cancellation_context, requests):
        pass
