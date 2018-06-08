import json
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from K8S_App_Shell_OS import *
from DeployVMReturnObj import *
import uuid
import time
global _k8s_context
global _attrib

class K8ShellDriver(ResourceDriverInterface):
    ######################
    # Boilerplates
    ######################
    # begin boilerplates
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.deployments = dict()
        self.deployments['Kubernetes Deploy Container From Image'] = self.deploy_img
        self.deployments['Kubernetes Deploy Container From File'] = self.deploy_file
        self.deployments['Kubernetes Fake Deploy'] = self.deploy_fake
        pass

    def initialize(self, context):
        pass

    def cleanup(self):
        pass
    # end boilerplates

    ######################
    # Helper Functions
    ######################
    # begin helpers
    def getKey(self, context):
        pak = ""
        cacert = ""
        CPAtts = context.resource.attributes

        with CloudShellSessionContext(context) as csapi:
            pak = csapi.DecryptPassword(CPAtts["Private Access Key URI"]).Value
            cacert = csapi.DecryptPassword(CPAtts["CA Cert URI"]).Value
        return (pak,cacert)

    # end helpers

    ######################
    # Cloud provider
    ######################
    # begin cp
    def Deploy(self, context, request=None, cancellation_context=None):
        app_request = json.loads(request)
        deployment_name = app_request['DeploymentServiceName']
        if deployment_name in self.deployments.keys():
            deploy_method = self.deployments[deployment_name]
            return deploy_method(context,request,cancellation_context)
        else:
            raise Exception('Could not find the deployment')

    def deploy_fake(self, context, request, cancellation_context):
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        attr = lrra
        attr.update(r["Attributes"])

        ro = DeployVMReturnObj(newName, uid, "127.0.0.1", "127.0.0.1", "", attr)

        return ro

    def deploy_img(self, context, request, cancellation_context):
        # parse inputs and create a uuid for container name
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        CPAtts = context.resource.attributes

        # store original details in new object
        attr = lrra
        attr.update(r["Attributes"])

        # app data dict to pass to Mike's code
        add = {}
        add["AppName"] = r["Attributes"]["App Name"]
        add["AppImg"] = r["Attributes"]["App Img"]
        add["AppDeployName"] = newName
        add["AppPort"] = r["Attributes"]["App Port"]
        add["AppRepl"] = r["Attributes"]["App Repl"]
        add["AppNamespace"] = r["Attributes"]["App Namespace"]
        add["AppType"] = "dict"
        add["AppSubType"] = "app"
        add["AppImgUpdate"] = ""
        add["AppSvcName"] = r["Attributes"]["App Service Name"]

        # run mike's code
        keys = self.getKey(context)
        pak = keys(0)
        cacert = keys(1)
        _k8s_context = K8S_APP_Shell_OS(add, pak, CPAtts["IP Address"], CPAtts["Port"], cacert)

        # change for shell deployment script add service name and service object
        svcObj = _k8s_context.shell_deployment_script(_k8s_context.AppName, _k8s_context.AppPort,
                                                           _k8s_context.AppImg, _k8s_context.AppType,
                                                           _k8s_context.AppRepl, _k8s_context.AppDeployName,
                                                           _k8s_context.AppNamespace,
                                                           _k8s_context.AppImgUpdate, "",
                                                           _k8s_context.AppSubType,
                                                           _k8s_context.AppSvcName)
        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], context.resource.attributes["IP Address"], "", attr)
        return ro
        pass

    def deploy_file(self, context, request, cancellation_context):
        # parse inputs and create a uuid for container name
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        newAddr = context.resource.attributes["IP Address"] + ":" + r["Attributes"]["App Port"]
        CPAtts = context.resource.attributes

        # store original details in new object
        attr = lrra
        attr.update(r["Attributes"])

        # app data dict to pass to Mike's code
        add = {}
        add["AppName"] = r["Attributes"]["App Name"]
        add["AppYamlFileName"] = r["Attributes"]["App File"]
        add["AppDeployName"] = newName
        add["AppNamespace"] = r["Attributes"]["App Namespace"]
        add["AppType"] = "yaml"
        add["AppSubType"] = "app"
        add["AppSvcName"] = r["Attributes"]["App Service Name"]
        _attrib = add
        
        keys = self.getKey(context)
        pak = keys(0)
        cacert = keys(1)

        _k8s_context = K8S_APP_Shell_OS(add, pak, CPAtts["IP Address"], CPAtts["Port"], cacert)
        _k8s_context.shell_health_check()

        # change for shell deployment script add service name and service object
        svcObj = _k8s_context.shell_deployment_script(_k8s_context.AppName, '', '', _k8s_context.AppType,'',
                                                      _k8s_context.AppDeployName,_k8s_context.AppNamespace, '',
                                                      _k8s_context.AppYamlFileName,_k8s_context.AppSubType,
                                                      _k8s_context.AppSvcName)

        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], context.resource.attributes["IP Address"], "", attr)

        return ro
        pass

    def PowerOn(self, context, ports):
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Online", "Powered On")
        pass

    def PowerOff(self, context, ports):
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Offline", "Powered Off")
        pass

    def PowerCycle(self, context, ports, delay):
        self.PowerOff(context, ports)
        time.sleep(delay)
        self.PowerOn(context, ports)
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        cpResource = context.resource
        cpName = cpResource.name
        cpResourceContext = cpResource.attributes
        rootAppName = context.remote_endpoints[0].fullname

        add = {}
        add["AppName"] = CPAtts["App Name"]
        add["AppDeployName"] = rootAppName
        add["AppNamespace"] = CPAtts["App Namespace"]
        add["AppSubType"] = "app"
        add["AppSvcName"] = CPAtts["App Service Name"]

        _k8s_context = K8S_APP_Shell_OS(add,  pak, CPAtts["IP Address"], CPAtts["Port"], cacert)

        deployed = False

        with CloudShellSessionContext(context) as csapi:
            csapi.WriteMessageToReservationOutput(context.reservation.reservation_id, "Waiting for completed K8S deployment...")
            while not deployed:
                statObj = _k8s_context.shell_health_check_script(rootAppName, CPAtts["App Namespace"], CPAtts["App Service Name"])
                
                if("Complete" not in statObj.Status):
                    time.sleep(30)
                else:
                    deployed = True
                    for p in statObj.Pods:
                        csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Pod', resourceName=p(2), resourceAddress=p(0), folderFullPath='', parentResourceFullPath=rootAppName, resourceDescription=p(1))
                    for v in statObj.Volumes:
                        csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Volume', resourceName=v(2), resourceAddress=v(1), folderFullPath='', parentResourceFullPath=rootAppName, resourceDescription=v(3))
                    eCt = 0
                    for e in statObj.Endpoints:
                        eName = "Endpoint " + str(eCt)
                        eAddr = e.Addresses[eCt] + ":" + e.Ports[eCt]
                        csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Endpoint', resourceName=eName, resourceAddress=eAddr, folderFullPath='', parentResourceFullPath=rootAppName, resourceDescription='')
                        eCt = eCt + 1
        return
        pass

    def destroy_vm_only(self, context, ports):
        CPAtts = context.resource.attributes
        newName = context.remote_endpoints[0].fullname

        keys = self.getKey(context)
        pak = keys(0)
        cacert = keys(1)

        add = {}
        add["AppName"] = CPAtts["App Name"]
        add["AppDeployName"] = newName
        add["AppNamespace"] = CPAtts["App Namespace"]
        add["AppSubType"] = "app"
        add["AppSvcName"] = CPAtts["App Service Name"]

        _k8s_context = K8S_APP_Shell_OS(add,  pak, CPAtts["IP Address"], CPAtts["Port"], cacert)
        _k8s_context.shell_teardown_script(_k8s_context.AppName, _k8s_context.AppNamespace,
                                           _k8s_context.AppSvcName)

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
    # end cp