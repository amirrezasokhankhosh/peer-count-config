import os
import yaml
import json

cwd = os.path.dirname(__file__)
ccp_folder_path = os.path.abspath(os.path.join(cwd, "../test-network/organizations"))

def edit_organizations(peers):
    res = {
        'Org${ORG}': {
            'mspid': 'Org${ORG}MSP', 
            'peers': [], 
            'certificateAuthorities': ['ca.org${ORG}.example.com']
            }
        }
    for peer_num in peers:
        res['Org${ORG}']["peers"].append(f"peer{peer_num}.org${{ORG}}.example.com")
    return res

def edit_peers(peers):
    res = {}
    for peer_num in peers:
        cfg = {'url': f'grpcs://localhost:${{P{peer_num}PORT}}', 
               'tlsCACerts': {'pem': "${PEERPEM}\n"}, 
               'grpcOptions': {'ssl-target-name-override': f'peer{peer_num}.org${{ORG}}.example.com', 
                               'hostnameOverride': f'peer{peer_num}.org${{ORG}}.example.com'
                               }
            }
        res[f"peer{peer_num}.org${{ORG}}.example.com"] = cfg
    return res

def edit_ccp(peers):
    file_path = os.path.join(ccp_folder_path, "ccp-template.yaml")
    file = open(file_path, 'r')
    content = yaml.safe_load(file)
    file.close()

    content["organizations"] = edit_organizations(peers)
    content["peers"] = edit_peers(peers)

    file = open(file_path, 'w')
    yaml.dump(content, file)
    file.close()

    file_path = os.path.join(ccp_folder_path, "ccp-template.json")
    file = open(file_path, "w")
    json.dump(content, file)
    file.close()
