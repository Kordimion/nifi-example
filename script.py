import requests
from xml.etree import ElementTree
import re

host = "http://localhost:8082";
nifiurl = f"{host}/nifi-api"
template_name = "filecloner"
template_filename = f"./{template_name}.xml"
parameter_context_name = f"{template_name}_context"

sftp_host = "sftp"
sftp_port = 22
sftp_user = "foo"
sftp_password = "pass"
sftp_sshkey_path = "/opt/nifi/nifi-current/ssh/id_rsa"
sftp_sshkey_passphrase = "pass"


def fetch_root_process_group_id():
    root_process_group_url = f"{nifiurl}/flow/process-groups/root"
    try:
        response = requests.get(root_process_group_url)
        if not response.ok:
            print(f"Can't get root process group id. Terminating...")
            exit(-1)

        json_response = response.json()
        id = json_response["processGroupFlow"]["id"]
        return id

    except requests.RequestException:
        print(f"Nifi-api at {nifiurl} is unreachable. Terminating...")
        exit(-1)

def upload_template(root_process_group_id):
    template_upload_url = f"{nifiurl}/process-groups/{root_process_group_id}/templates/upload"

    form_data = {
        "template": open(template_filename, 'rb')
    }

    response = requests.post(template_upload_url, files=form_data)
    return response

def get_template_id_from_resources(template_name:str):
    resources_url = f"{nifiurl}/resources"
    response = requests.get(resources_url)
    if not response.ok:
        print("Error: Unable to fetch resources")
        exit(-1)

    json_response = response.json()
    try:
        identifier = [x["identifier"] for x in json_response["resources"] if x["name"] == template_name][0]
        id_without_prefix = identifier[11:]
        return id_without_prefix
    except IndexError:
        print(f"Error: not found {template_name} resource")
        exit(-1)

def upsert_template_id(root_process_group_id: int):
    response = upload_template(root_process_group_id)

    if response.ok:
        m = re.search(r'<id>(.*?)</id>', response.text)
        if m:
            value = m.group(1)
            return value
        else:
            print(response.content)
            exit(-1)
    else:
        template_exists = response.status_code == 409
        if template_exists:
            id = get_template_id_from_resources(template_name)
            return id
        else:
            print("Error: Unable to upload template")

            print("Status code:", response.status_code)
            print("Response text:", response.text)

            exit(-1)

def create_process_group_from_template(root_process_group_id, template_id):
    url = f"{nifiurl}/process-groups/{root_process_group_id}/template-instance"

    json_data = {
        'originX': 0,
        'originY': 0,
        'templateId': template_id,
    }

    response = requests.post(url, json=json_data)

    if not response.ok:
        print("Error: Unable to instantiate a process group from template")

        print("url: ", url)
        print("Status code:", response.status_code)
        print("Response text:", response.text)

        exit(-1)
    
    return response.json()


def create_and_attach_parameter_context(flow_dto):
    process_group_id = flow_dto["flow"]["processGroups"][0]["id"]

    parameter_context_url = f"{nifiurl}/parameter-contexts"

    form_data = {
        "revision":{
            "version": 0
        },
        "component": {
            "name": parameter_context_name,
            "description": f"parameter group for {template_name} template",
            "parameters": [{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.host",
                    "sensitive": False,
                    "value": sftp_host,
                }
            },{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.pass",
                    "sensitive": True,
                    "value": sftp_password,
                }
            },{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.port",
                    "sensitive": False,
                    "value": sftp_port,
                }
            },{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.sshkey.passphrase",
                    "sensitive": True,
                    "value": sftp_sshkey_passphrase,
                }
            },{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.sshkey.path",
                    "sensitive": False,
                    "value": sftp_sshkey_path,
                }
            },{
                "canWrite": True,
                "parameter": {
                    "name": "sftp.user",
                    "sensitive": False,
                    "value": sftp_user,
                }
            }]
        }
    }

    response = requests.post(parameter_context_url, json=form_data)

    if not response.ok:
        print("Error: Unable to instantiate a parameter context")

        print("url: ", parameter_context_url)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        exit(-1)

    parameter_context_id = response.json()["id"]
    parameter_context_url = f"{nifiurl}/process-groups/{process_group_id}/parameter-context"
    old_response = response
    response = requests.post(parameter_context_url, json={"id": parameter_context_id})
    if not response.ok:
        print("Error: Unable to bind a parameter context")

        print("url: ", parameter_context_url)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        exit(-1)

    return old_response

def start_process_group(flow_dto):
    process_group_id = flow_dto["flow"]["processGroups"][0]["id"]

    process_group_start_url = f"{nifiurl}/flow/process-groups/{process_group_id}/controller-services"
    json_data = {
        "id": process_group_id,
        "state": "ENABLED"
    }
    response = requests.put(process_group_start_url, json=json_data)

    if not response.ok:
        print("Error: Unable to start process group")

        print("url: ", process_group_start_url)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        exit(-1)
    pass

if __name__ == "__main__":
    root_process_group_id = fetch_root_process_group_id()
    # print(f"root id: {root_process_group_id}")
    template_id = upsert_template_id(root_process_group_id)
    # print(f"template id: {template_id}")
    flow_dto = create_process_group_from_template(root_process_group_id, template_id)
    # print(f"flow dto: {flow_dto}")
    # step4: creating and attaching parameter context to the process group
    parameter_context = create_and_attach_parameter_context(flow_dto)
    # step5: starting the process group
    start_process_group(flow_dto)

    print(f"Script succeedeed. check nifi at {host}/nifi")

