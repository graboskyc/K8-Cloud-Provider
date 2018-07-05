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
    def _getKey(self, context):
        # private access key and cpa cert are stored as a encrypted uri on the cloud provider
        # pull them from cloud provider and decrypt and return
        pak = ""
        cacert = ""
        CPAtts = context.resource.attributes

        with CloudShellSessionContext(context) as csapi:
            pak = csapi.DecryptPassword(CPAtts["Private Access Key URI"]).Value
            cacert = csapi.DecryptPassword(CPAtts["CA Cert URI"]).Value
        print("Private Access Key URI: ")
        pprint(pak)
        print("CA Cert URI: ")
        pprint(cacert)
        return {"Private Access Key URI": pak,"CA Cert URI": cacert}

    def _storeappDict(self, appDict, resourceName):
        addfileName = resourceName +'.txt'
        with open(addfileName, 'w') as f:
            f.write(json.dumps(appDict))
            f.close()

    def _getappDict(self, resourceName):
        addfileName = resourceName +'.txt'
        appDict = {}
        try:
            appDict = json.load(open(addfileName))
        except IOError as e:
            print "Error: File " + addfileName + "does not appear to exist.", e
            logging.error("File does not appear to exist.", e)
            # app attributes
        return appDict
    
    def _status_decode(self, statObj):
        print("Status: ")
        pprint(statObj["Status"])
        statusDecode=False
        for item in statObj["Status"]:
            if item.find("Fail") != -1 or item.find("Success") != -1:
                statusDecode=True
        return statusDecode
    # end helpers

    ######################
    # Cloud provider
    ######################
    # FLOW should be Deploy->PowerOn->Refresh IP all stateless!

    # begin cp
    def Deploy(self, context, request=None, cancellation_context=None):
        # figure out if this is from image, from file, or test/dummy
        # run correct function based on that which all have different attributes
        app_request = json.loads(request)
        deployment_name = app_request['DeploymentServiceName']
        if deployment_name in self.deployments.keys():
            deploy_method = self.deployments[deployment_name]
            return deploy_method(context,request,cancellation_context)
        else:
            raise Exception('Could not find the deployment')

    def deploy_fake(self, context, request, cancellation_context):
        # quick testing method
        r = json.loads(request)
        lrra = r["LogicalResourceRequestAttributes"]
        uid = str(uuid.uuid4())[:8]
        newName = r["UserRequestedAppName"] + "-" + uid
        attr = lrra
        attr.update(r["Attributes"])

        ro = DeployVMReturnObj(newName, uid, "127.0.0.1", "127.0.0.1", "", attr)

        return ro

    def deploy_img(self, context, request, cancellation_context):
        # deploy from image
        
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

        self._storeappDict(add, newName)
        # _attrib = add
        pak = ""
        cacert = ""

        # get keys
        keys = self._getKey(context)
        pak = keys["Private Access Key URI"]
        cacert = keys["CA Cert URI"]
        print("Private Access Key URI: ")
        pprint(pak)
        print("CA Cert URI: ")
        pprint(cacert)

        _k8s_context = K8S_APP_Shell_OS(add, pak, CPAtts["IP Address"], CPAtts["Port"], cacert)

        # change for shell deployment script add service name and service object
        svcStatusObj = _k8s_context.shell_deployment_script(_k8s_context.AppName, _k8s_context.AppPort,
                                                           _k8s_context.AppImg, _k8s_context.AppType,
                                                           _k8s_context.AppRepl, _k8s_context.AppDeployName,
                                                           _k8s_context.AppNamespace,
                                                           _k8s_context.AppImgUpdate, "",
                                                           _k8s_context.AppSubType,
                                                           _k8s_context.AppSvcName)
        print("Service Status object: ")
        pprint(svcStatusObj)
        # Return to cloudshell what it expects
        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], context.resource.attributes["IP Address"], "", attr)
        return ro
        pass

    def deploy_file(self, context, request, cancellation_context):
        # deploy from YAML file instead

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
        add["NewName"] = newName
        _attrib = add
        pak=""
        cacert=""
        # get keys
        keys = self._getKey(context)
        self._storeappDict(add, newName)
        pak = keys["Private Access Key URI"]
        cacert = keys["CA Cert URI"]
        print("Private Access Key URI: ")
        pprint(pak)
        print("CA Cert URI: ")
        pprint(cacert)
        _k8s_context = K8S_APP_Shell_OS(add, pak, CPAtts["IP Address"], CPAtts["Port"], cacert)
        #_k8s_context.shell_health_check_script()

        # change for shell deployment script add service name and service object
        svcStatusObj = _k8s_context.shell_deployment_script(_k8s_context.AppName, '', '', _k8s_context.AppType,'',
                                                      _k8s_context.AppDeployName,_k8s_context.AppNamespace, '',
                                                      _k8s_context.AppYamlFileName,_k8s_context.AppSubType,
                                                      _k8s_context.AppSvcName)
        print("Service Status Object: ")
        pprint(svcStatusObj)
        # build return object to CloudShell
        ro = DeployVMReturnObj(newName, uid, context.resource.attributes["IP Address"], context.resource.attributes["IP Address"], "", attr)

        return ro
        pass

    def PowerOn(self, context, ports):
        # doesn't do anything now
        # just change icon on resource 
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Online", "Powered On")
            rd = cloudshell_session.GetResourceDetails(context.remote_endpoints[0].fullname)
            if (len(rd.ChildResources) == 0):
                self.discover(context, ports)
        pass

    def PowerOff(self, context, ports):
        # doesn't do anything now
        # just change icon on resource 
        with CloudShellSessionContext(context) as cloudshell_session:
            cloudshell_session.SetResourceLiveStatus(context.remote_endpoints[0].fullname, "Offline", "Powered Off")
        pass

    def PowerCycle(self, context, ports, delay):
        self.PowerOff(context, ports)
        time.sleep(delay)
        self.PowerOn(context, ports)
        pass

    

    def remote_refresh_ip(self, context, ports, cancellation_context):
        with CloudShellSessionContext(context) as cloudshell_session:
            rd = cloudshell_session.GetResourceDetails(context.remote_endpoints[0].fullname)
            if (len(rd.ChildResources) == 0):
                self.discover(context, ports)

    # this should be restructured into the K8S App Model shell instead of the cloud provider shell
    # this technical debt will be done during official cloud provider support in CS 9.0
    def discover(self, context, ports):
        # called after deployed and powered on
        # here is how we will discover sub-resources

        # figure out name of cloud provider and the deployed app name
        cpResource = context.resource
        cpName = cpResource.name
        cpResourceContext = cpResource.attributes
        #resID = context.reservation.reservation_id
        CPAtts = context.resource.attributes
        print("Atributes: ")
        pprint(CPAtts)
        rootAppName = context.remote_endpoints[0].fullname
        add = self._getappDict(rootAppName)
        # pass minimal detauls to mike's code
        # add = {}
        # add["AppName"] = CPAtts["App Name"]
        # add["AppDeployName"] = CPAtts["App Name"]
        # add["AppNamespace"] = CPAtts["App Namespace"]
        # add["AppSubType"] = "app"
        # add["AppSvcName"] = CPAtts["App Service Name"]

        # _attrib = add
        pak = ""
        cacert = ""
        print("App Attributes: ")
        pprint(add)
        # get keys
        keys = self._getKey(context)

        pak = keys["Private Access Key URI"]
        cacert = keys["CA Cert URI"]
        print("Private Access Key URI: ")
        pprint(pak)
        print("CA Cert URI: ")
        pprint(cacert)

        _k8s_context = K8S_APP_Shell_OS(add,  pak, CPAtts["IP Address"], CPAtts["Port"], cacert)

        deployed = False
        # we dont know if deployment is done
        # so keep polling Mike's code to see when it is every 30 seconds
        with CloudShellSessionContext(context) as csapi:

            #csapi.WriteMessageToReservationOutput(resID,"Waiting for completed K8S deployment...")
            while not deployed:
                statObj = _k8s_context.shell_health_check_script(_k8s_context.AppName, _k8s_context.AppNamespace,
                                                                 _k8s_context.AppSvcName)
                errorFN = "C:\\temp\\error_" + rootAppName + ".txt"
                with open(errorFN, 'a') as f:
                    f.write("Status Object:\n"+json.dumps(statObj)+"\n\n")
                    f.close()
                if not self._status_decode(statObj):
                    # not finished deploying
                    time.sleep(30)
                else:
                    # everything is done
                    # iterate over each sub object returned by mike's code to create the pods, volumes, and endpoints
                    # try/ignores are in case this is re-run due to new pods added.
                    # that will ignore existing things with same name
                    deployed = True

                    with open(errorFN, 'a') as f:
                        f.write("Using "+rootAppName +"\n\n-----\n\n")
                        f.close()
                    for p in statObj["Pods"]:
                        try:
                            csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Pod', resourceName=p[2], resourceAddress=p[0], parentResourceFullPath=rootAppName, resourceDescription=p[1])
                        except:
                            with open(errorFN, 'a') as f:
                                f.write("parent: " + rootAppName + " resourceName: " + p[2] + " resourceAddress: " + p[0] + " resourceDescription: " + p[1] + "\n")
                                f.write("Error with pods\n"+json.dumps(statObj)+"\n\n")
                                f.close()
                            pass
                    for v in statObj["Volumes"]:
                        try:
                            csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Volume',
                                                 resourceName=v[1], resourceAddress=v[1], folderFullPath='',
                                                 parentResourceFullPath=rootAppName, resourceDescription=v[2])
                        except:
                            with open(errorFN, 'a') as f:
                                f.write("Error with vols\n"+json.dumps(statObj)+"\n\n")
                                f.close()
                            pass
                    eCt = 0
                    for e in statObj["Endpoints"]:
                        try:
                            eName = "service-endpoint-" + str(eCt)
                            eAddr = e[1] + ":" + e[0]
                            csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Endpoint',
                                                 resourceName=eName, resourceAddress=eAddr, folderFullPath='',
                                                 parentResourceFullPath=rootAppName, resourceDescription='')
                        except:
                            with open(errorFN, 'a') as f:
                                f.write("Error with endpoints\n"+json.dumps(statObj)+"\n\n")
                                f.close()
                            pass
                        eCt = eCt + 1
                    for s in statObj["Secrets"]:
                        try:
                            csapi.CreateResource(resourceFamily='K8S Objects', resourceModel='K8S Secret', resourceName=s[1], resourceAddress=s[0], parentResourceFullPath=rootAppName, resourceDescription=s[1])
                        except:
                            with open(errorFN, 'a') as f:
                                f.write("parent: " + rootAppName + " resourceName: " + s[1] + " resourceAddress: " + s[0] + " resourceDescription: " + s[1] + "\n")
                                f.write("Error with secrets\n"+json.dumps(statObj)+"\n\n")
                                f.close()
                            pass
        return
        pass

    def destroy_vm_only(self, context, ports):
        # figure out name of cloud provider and the deployed app name
        cpResource = context.resource
        cpName = cpResource.name
        cpResourceContext = cpResource.attributes
        CPAtts = context.resource.attributes
        print("Atributes: ")
        pprint(CPAtts)
        rootAppName = context.remote_endpoints[0].fullname
        # pass minimal detauls to mike's code
        # get keys
        keys = self._getKey(context)
        add = self._getappDict(rootAppName)
        print("App Attributes: ")
        pprint(add)
        pak = keys["Private Access Key URI"]
        cacert = keys["CA Cert URI"]
        print("Private Access Key URI: ")
        pprint(pak)
        print("CA Cert URI: ")
        pprint(cacert)

        #add = {}
        #add["AppName"] = CPAtts["App Name"]
        #add["AppDeployName"] = CPAtts["App Name"]
        #add["AppNamespace"] = CPAtts["App Namespace"]
        #add["AppSubType"] = "app"
        #add["AppSvcName"] = CPAtts["App Service Name"]

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
