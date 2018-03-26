import json
import subprocess
import sys
from pprint import pprint
from kubernetes import client, config
from kubernetes.client.rest import ApiException

########################################################################################
#  K8S_Shell_AWS Package mpw v0.933
#  There are some scripts that run from Python shell Linux/Windows command line
#  But mainly this is K8S and Openshift API
#  Next step is to move it to a Driver Interface to a TOSCA Oasis standard driver set
#
#  Disclaimer - Currently this has only been tested on Ubuntu 17 command line
#     Use at own Risk, this package only works on AWS so far
#      Future versions will work on GKE
#    Prerequisites
#       Install Kubernetes- both kops and kubectl are required to be working and
#       configured from the
#        Install AWS Client - need AWS client configured to access your AWS Account
#     There is a mixing of some Docker concepts here as we perform Docker build and
#     Deployments to Kubernetes pods for Docker built applications
#     Some Docker examples are provided
#     The broader goal is to move the Docker build and deployments to an App based
#     TOSCA Shell thus having a cloud provider Shell and a Docker App Deployment Shell
#
########################################################################################
class K8S_APP_Shell_OS(object):
    """K8S_App_Shell_OS.py
    #  K8S_Shell_AWS Package mpw v0.7
    #  uses the attributes in JSON file to buildout and teardown cluster
    #  and deploy container apps and execute commands on container
    Attributes:
        AppName:
        AppTag:
        AppImg:
        AppDeployName:
        AppNamespace:
        AppPort:
        ApplRepl:
        AppType:
    """
    def __init__(self, serviceun, serviceprivatekey, servicepublickey):
        self.serviceUsername = serviceun
        self.servicePrivateKey = serviceprivatekey
        self.servicePublicKey = servicepublickey
        
        config.load_kube_config()
        self.extensions_v1beta1 = client.ExtensionsV1beta1Api()

    def shell_teardown_script(self, appname, appns):
        delete_deployment(self.extensions_v1beta1, appname, appns)
        docker_stop_all(self)
        list_projects_pods_all()
        #list_pods_all()
        list_projects_all()
        docker_list(self)

    def shell_startup_script(self):
        pass

    def shell_health_check(self):
        get_ClusterDetails(self)
        get_DeploymentDetails(self)
        docker_version(self)
        docker_list(self)

    def shell_deployment_script(self, appname, appns, appport, appimg, apptype, apprepl, appdepname, appdir):
        #docker_pull(appname)
        docker_build(appdir)
        #docker_deploy(appname)
        deployment = create_deployment_object(appname, appport, appimg, apptype, appreplm appdepname)
        create_deployment(self.extensions_v1beta1, deployment, appns)
        update_deployment(self.extensions_v1beta1, deployment, appimg, appdepname, appns)
        list_projects_pods_all()
        #list_pods_all()
        list_projects_all()
        docker_list(self)

###########################################################################################################
# K8S Command helpers and builders provide an ability to wrap Command line and API calls for K8S
# will create helper class
###########################################################################################################
def k8s_command_builder(self, command, command2):

        '''
        Kubernetes Command Builder mpw v0.7
        accepts kubernetes cluster command
        returns custom command based on JSON values
        :param self, command, command2:resp = None
        :return:
        '''
        # create sub-command strings
        # return fully qualified kubernetes shell commands
        return {
            'version' : 'docker' + ' --' + command,
            'build' : 'docker ' + command + ' ' + command2,
            'deploy' : 'kubectl apply ' + '-f ' + command2,
            'run' : 'kubectl ' + command + ' ' + '--image=' + command2,
            'list' : 'docker image ls',
            'cluster-info': 'kubectl ' + command,
            'get deployments' : 'kubectl ' + command
            }.get(command, "")

def k8s_command_helper_sys(cmd):
        '''#  K8S_Shell_Driver Package mpw
        mpw v0.7
        Kubernetes Command Helper - sends shell scripts to Shell
        Works at Linux command line or Powershell
        Accepts filename and path and executes shell script
        as subprocess shell command
        :param cundeploy_k8s_apps(md:
        :return:
        '''
        print cmd
        try:
            retcode = subprocess.call([cmd])
            if retcode < 0:
                print >> sys.stderr, "Child was terminated by signal", -retcode
            else:
                print >> sys.stderr, "Child returned", retcode
        except OSError as e:
            print >> sys.stderr, "Execution failed:", e


def k8s_command_helper(cmd):
        '''
        mpw v0.7
        Kubernetes Command Helper - sends non-executable
        shell commands to a command Shell
        Works at Linux command line or Powershell
        Accepts any non- OS executable command
        and sends it as subprocess shell command
        shell = True means this will routine handle
        :param cmd:
        :return:
        '''
        print cmd
        try:
            retcode = subprocess.call([cmd], shell=True)
            if retcode < 0:
                print >> sys.stderr, "Child was terminated by signal", -retcode
            else:
                print >> sys.stderr, "Child returned", retcode
        except OSError as e:
            print >> sys.stderr, "Execution failed:", e

############################################################################################################
#
# K8S API clls to deploy and undeploy K8S apps based on Deployment Object and App Attributes
#
############################################################################################################

def create_deployment_object(app_name, app_port, app_img, app_type, app_repl, app_deploy_name):
    '''
    Create a k8s deployment objec based on app parameters using k8s api
    :param app_name:
    :param app_img:
    :param app_port:
    :param app_tag:
    :param app_repl:
    :param app_deploy_name:
    :return:
    '''
    # Configureate Pod template container
    iPort = int(app_port)
    iRepl = int(app_repl)
    container = client.V1Container(
        name=app_name,
        image=app_img,
        ports=[client.V1ContainerPort(container_port=iPort)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={app_type : app_name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=iRepl,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=app_deploy_name),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment, app_namespace):
    '''
    Send deployment request to k8s api using deployment object
    :param api_instance:
    :param deployment:
    :param app_namespace:
    :return:
    '''
    # Create deployement
    try:
        api_response = api_instance.create_namespaced_deployment(
            body=deployment,
            namespace=app_namespace)
        print("Deployment created. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Deployment failed. status='%s'" % e)


def update_deployment(api_instance, deployment, app_img, app_deploy_name, app_namespace):
    '''
    update an existing deployment via k8s api eitt  deployment object
    :param api_instance:
    :param deployment:
    :param app_img:
    :param app_deploy_name:
    :param app_namespace:
    :return:
    '''
    deployment.spec.template.spec.containers[0].image = app_img
    try:
        api_response = api_instance.patch_namespaced_deployment(
            name=app_deploy_name,
            namespace=app_namespace,
            body=deployment)
        print("Deployment updated. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Deployment update failed. status='%s'" % e)


def delete_deployment(api_instance, app_deploy_name, app_namespace):
    '''
    Delete an existing deployment using k8s api request and deployment object
    :param api_instance:
    :param app_deploy_name:
    :param app_namespace:
    :return:
    '''
    try:
        api_response = api_instance.delete_namespaced_deployment(
            name=app_deploy_name,
            namespace=app_namespace,
            body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
        print("Deployment deleted. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Deployment deletion failed. status='%s'" % e)

def create_project(api_instance, app_namespace):
    '''
    create a project(openshift) or namaspace(k8s)
    :param api_instance:
    :param app_namespace:
    :return:
    '''
    namespace_body= client.V1Namespace()
    try:
        api_response = api_instance.create_namespaced_deployment(
            namespace=app_namespace,
            body=namespace_body)
        print("Namespace created. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Namespace creation failed. status='%s'" % e)


def delete_project(api_instance, app_namespace):
    '''
    Deletes an existing project(Openshift) or NameSpace(K8S)
    :param api_instance: 
    :param app_namespace: 
    :return: 
    '''
    try:
        api_response = api_instance.delete_namespace(
            name=app_namespace,
            body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
        print("Project namespace deleted. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Project namespace deletion failed. status='%s'" % e)

def create_pod(api_instance, app_namespace):
    '''
    create a namespaced pod
    :param api_instance:
    :param app_namespace:
    :return:
    '''
    pod_body= client.V1Pod()
    try:
        api_response = api_instance.create_namespaced_pod(
            namespace=app_namespace,
            body=pod_body)
        print("Pod created. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Pod creation failed. status='%s'" % e)


def delete_pod(api_instance, app_pod, app_namespace):
    '''
    Deletes an existing namespaced pod
    :param api_instance:
    :param app_namespace:
    :return:
    '''
    try:
        api_response = api_instance.delete_namespaced_pod(
            name=app_pod,
            namespace=app_namespace,
            body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
        print("Project namespace deleted. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Project namespace deletion failed. status='%s'" % e)

def create_node(api_instance, app_node):
    '''
    create a node
    :param api_instance:
    :param app_namespace:
    :return:
    '''
    node_body= client.V1Node()
    try:
        api_response = api_instance.create_node(
            name=app_node,
            body=node_body)
        print("Node created. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Node creation failed. status='%s'" % e)


def delete_node(api_instance, app_node):
    '''
    Deletes an existing node
    :param api_instance:
    :param app_namespace:
    :return:
    '''
    try:
        api_response = api_instance.delete_node(
            name=app_node,
            body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
        print("node deleted. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("node deletion failed. status='%s'" % e)

def list_projects_pods_all():
    '''
    Lists all projects and pods for all namespaces using K8S and OC API
    :return:
    '''
    from openshift import config, client
    import kubernetes
    oclient_config = config.new_client_from_config()
    oapi = client.OapiApi(oclient_config)
    kclient_config = config.new_client_from_config()
    api = kubernetes.client.CoreV1Api(kclient_config)
    project_list = oapi.list_project()
    print("Listing All Openshift Projects with Pods:")
    for project in project_list.items:
        project_name = project.metadata.name
        print('project: '+ project_name)
        pod_list = api.list_namespaced_pod(project_name)
        for pod in pod_list.items:
            print('    pod: '+ pod.metadata.name)

def list_projects_all():
    '''
    Lists all projects for all namespaces using OC API
    :return:
    '''
    from openshift import config, client
    oclient_config = config.new_client_from_config()
    oapi = client.OapiApi(oclient_config)
    print("Listing All Openshift Projects:")
    project_list = oapi.list_project()
    for project in project_list.items:
        project_name = project.metadata.name
        print('project: '+ project_name)

def list_pods_all():
    '''
    Lists all pods with IPs for all namespaces using k8s API
    :return:
    '''
    kclient_config = config.new_client_from_config()
    api = client.CoreV1Api(kclient_config)
    print("Listing K8S Pods with their IPs:")
    ret = api.list_pod_for_all_namespaces()
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def docker_pull(self, appname):
    '''
    pulls a docker image
    :param self:
    :return:
    '''
    import docker
    client = docker.from_env()
    print "Pulling container " + appname
    image = client.images.pull(appname)
    print image.id

def docker_build(self, appdir):
    '''
    builds a container in a directory with BuildFile
    :param self:
    :return:
    '''
    print "Building container in " + appdir
    k8s_cmd = k8s_command_builder(self, "build", appdir)
    k8s_command_helper(k8s_cmd)

def docker_deploy(self, appname):
    '''
    deploys a container
    :param self:
    :return:
    '''
    import docker
    client = docker.from_env()
    print "Deploying container " + appname
    print client.containers.run(appname)

def docker_list(self):
    '''
    list all docker containers
    :param self:
    :return:
    '''
    import docker
    client = docker.from_env()
    print "List of all containers: "
    for container in client.containers.list():
        print container.id

def docker_stop_all(self):
    '''
    stop all docker containers
    :param self:
    :return:
    '''
    import docker
    client = docker.from_env()
    print "Stopping all containers:"
    for container in client.containers.list():
        container.stop()

def k8s_export_config():
    k8s_command_helper_sys("./k8s-reconfig.sh")

def install_docker_ce():
    pass

def install_AWS_Client():
    k8s_command_helper_sys("./install-aws-client.sh")

def docker_version(self):
    '''
    Print Docker Version details
    :param self:
    :return:
    '''
    import docker
    client = docker.from_env()
    VersionDict = client.version(self)
    print "Docker Version is: " + VersionDict["Version"]
    print "Docker API Version is: " + VersionDict["ApiVersion"]
    print "Kernel Version is: " + VersionDict["KernelVersion"]

def get_ClusterDetails(self):
    k8s_cmd = k8s_command_builder(self, "cluster-info", "")
    k8s_command_helper(k8s_cmd)

def get_DeploymentDetails(self):
    k8s_cmd = k8s_command_builder(self, "get deployments", "")
    k8s_command_helper(k8s_cmd)

def start_KubeRun(self):
    k8s_cmd = k8s_command_builder(self, "run", "")
    k8s_command_helper(k8s_cmd)

if __name__ == "__main__":
    try:
        k8s_data = json.load(open('K8S_App_Data_OS.json'))
    except IOError:
        print "Error: File does not appear to exist."

    k8s_shell = K8S_APP_Shell_OS()
    k8s_shell.shell_startup_script()
    k8s_shell.shell_health_check()
    # appname, appns, appport, appimg, apptype, apprepl, appdepname
    k8s_shell.shell_deployment_script(k8s_data["AppName4"], k8s_data["AppNamespace4"], k8s_data["AppPort4"], k8s_data["AppImg4"], k8s_data["AppType4"], k8s_data["AppRepl4"], k8s_data["AppDeployName4"], k8s_data["AppDir1"])
    # appname, appns
    k8s_shell.shell_teardown_script(k8s_data["AppName4"], k8s_data["AppNamespace4"])