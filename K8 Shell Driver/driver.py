import json
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from K8S_App_Shell_OS import *
from DeployVMReturnObj import *
import uuid
global _k8s_context
global _attrib
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

    def getKey(self):
        # hack for now
        with open('c:\\temp\\tempkey.key', 'r') as content_file:
            api_ca_cert = content_file.read()

        return api_ca_cert

    def parseK8sRetObj(self, svcObj, serviceName):
        addList = []
        portList = []
        print('service object: ')
        pprint(svcObj)
        print('service name: ' + serviceName)

        for item in svcObj.items:

            if item.metadata.name == serviceName:

                for subset in item.subsets:

                    service_port = subset.ports
                    service_address = subset.addresses
                    if service_address is None:
                        service_address = subset.not_ready_addresses

                    for addrObj in service_address:
                        addList.append(addrObj.ip)

                    for portObj in service_port:
                        portList.append(portObj.port)

        return {"Addresses":addList, "Ports":portList}



    def deploy_img(self, context, request, cancellation_context):
        # parse inputs and create a uuid for container name
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        attr = {'Password':lrra["Password"],"User":lrra["User"],"Public IP":lrra["Public IP"]}
        newAddr = context.resource.attributes["IP Address"] + ":" + r["Attributes"]["App Port"]
        CPAtts = context.resource.attributes

        # hack for now
        api_ca_cert = self.getKey()

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
        pak = ""
        with CloudShellSessionContext(context) as csapi:
            pak = csapi.DecryptPassword(CPAtts["Private Access Key"]).Value

        _k8s_context = K8S_APP_Shell_OS(add, "primary", pak, CPAtts["IP Address"], CPAtts["Port"], api_ca_cert)
        _k8s_context.shell_health_check()

        # change for shell deployment script add service name and service object
        svcStr = _k8s_context.shell_deployment_script(_k8s_context.AppName, _k8s_context.AppPort,
                                                           _k8s_context.AppImg, _k8s_context.AppType,
                                                           _k8s_context.AppRepl, _k8s_context.AppDeployName,
                                                           _k8s_context.AppNamespace,
                                                           _k8s_context.AppImgUpdate, "",
                                                           _k8s_context.AppSubType,
                                                           _k8s_context.AppSvcName)
        svcObj = self.parseK8sRetObj(svcStr, r["Attributes"]["App Service Name"])
        newAddr = svcObj["Addresses"][0] + ":" + svcObj["Ports"][0]
        ro = DeployVMReturnObj(newName, uid, CPAtts["IP Address"], newAddr, "", attr)

        return ro
        pass

    def deploy_file(self, context, request, cancellation_context):
        # parse inputs and create a uuid for container name
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        attr = {'Password':lrra["Password"],"User":lrra["User"],"Public IP":lrra["Public IP"]}
        newAddr = context.resource.attributes["IP Address"] + ":" + r["Attributes"]["App Port"]
        CPAtts = context.resource.attributes

        # hack for now
        api_ca_cert = self.getKey()

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
        pak = ""
        with CloudShellSessionContext(context) as csapi:
            pak = csapi.DecryptPassword(CPAtts["Private Access Key"]).Value
        #create temp file
        print 'Building a file name yourself:'
        newfilename = newName
        filename = 'c:/temp/'+ newfilename + '.txt'
        json.dump(_attrib, open(filename, 'w'))

        _k8s_context = K8S_APP_Shell_OS(add, "primary", pak, CPAtts["IP Address"], CPAtts["Port"], api_ca_cert)
        _k8s_context.shell_health_check()

        # change for shell deployment script add service name and service object
        svcObj = _k8s_context.shell_deployment_script(_k8s_context.AppName, '', '', _k8s_context.AppType,'',
                                                      _k8s_context.AppDeployName,_k8s_context.AppNamespace, '',
                                                      _k8s_context.AppYamlFileName,_k8s_context.AppSubType,
                                                      _k8s_context.AppSvcName)
        #svcObj = self.parseK8sRetObj(svcStr, r["Attributes"]["App Service Name"])
        newAddr = svcObj["Addresses"][0] + ":" + str(svcObj["Ports"][0])

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
        self.PowerOff(context, ports)
        time.sleep(delay)
        self.PowerOn(context, ports)
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        return
        pass

    def destroy_vm_only(self, context, ports):
        # parse inputs and create a uuid for container name
        CPAtts = context.resource.attributes
        print("context resources: ")
        pprint(CPAtts)
        newName = context.remote_endpoints[0].fullname
        print("request resources: ")
        newfilename = newName
        filename = 'c:/temp/' + newfilename + '.txt'
        _attrib = json.load(open(filename))
        #retrieve attributes from file
        add = _attrib
        #add["AppName"] = context.remote_endpoints[0]
        #add["AppType"] = "yaml"
        #add["AppSubType"] = "app"
        #add["AppSvcName"] = "mysql-service"
        #add["AppNamespace"] = "production"
        #add["AppDeployName"] = "mysql"
        #add["AppYamlFileName"] = "mysql.yaml"
        print("address dict: ")
        pprint(add)

        # hack for now
        api_ca_cert = self.getKey()

        pak = ""
        with CloudShellSessionContext(context) as csapi:
            pak = csapi.DecryptPassword(CPAtts["Private Access Key"]).Value
        _k8s_context = K8S_APP_Shell_OS(add, "primary", pak, CPAtts["IP Address"], CPAtts["Port"], api_ca_cert)
        _k8s_context.shell_teardown_script("primary", _k8s_context.AppName, _k8s_context.AppSvcName,
                                           _k8s_context.AppNamespace)

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
