
class DeployVMReturnObj:
    def __init__(self, name, uuid, cpName, address, publicIP):
        self.vm_name = name
        self.vm_uuid = uuid
        self.cloud_provider_resource_name = cpName
        self.auto_power_off = False
        self.wait_for_ip = False
        self.auto_delete = True
        self.autoload = False
        self.deployed_app_address = address
        self.public_ip = publicIP
        