import json
import datetime


def load_data():
    projectfile = "projects.json"
    memberfile = "members.json"
    allocationfile = "allocations.json"

    def date_hook(json_dict):
        for key, value in json_dict.items():
            if 'date' in key and value != "None":
                json_dict[key] = datetime.datetime.strptime(value, "%d-%m-%Y")
        return json_dict
    with open(projectfile, 'r') as pfile:
        projects = json.load(pfile, object_hook=date_hook)
    with open(memberfile, 'r') as mfile:
        members = json.load(mfile, object_hook=date_hook)
    with open(allocationfile, 'r') as afile:
        allocations = json.load(afile, object_hook=date_hook)
    return projects, members, allocations
