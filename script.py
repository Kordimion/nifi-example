import requests
import json

nifiurl = "http://localhost:8082/nifi-api"
template_name = "filecloner"
template_filename = f"./{template_name}.xml"

def fetch_root_process_group_id():
    root_process_group_url = f"{nifiurl}/flow/process-groups/root"
    response = requests.get(root_process_group_url)
    if not response.ok:
        print("Error: Unable to fetch root process group id")
        exit(-1)

    json_response = response.json()
    id = json_response["processGroupFlow"]["id"]
    return id

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
        json_response = response.json()
        id = json_response["id"]
        return id
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
    
    return json.dumps(response.json(), indent=4)



if __name__ == "__main__":
    root_process_group_id = fetch_root_process_group_id()
    print(f"root id: {root_process_group_id}")
    template_id = upsert_template_id(root_process_group_id)
    print(f"template id: {template_id}")
    flow_dto = create_process_group_from_template(root_process_group_id, template_id)
    print(f"flow dto: {flow_dto}")



# step1: getting root process group id.

# step2: uploading template file into the nifi

# step3: creating new process group out of that template

# step4: starting new process group


