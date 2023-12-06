import os
import yaml

cwd = os.path.dirname(__file__)
crypto_cfg_path = os.path.abspath(os.path.join(cwd, '../test-network/organizations/cryptogen'))

def edit_crypto_cfg(orgs, count):
    for org_name in orgs:
        file_path = os.path.join(crypto_cfg_path, f"crypto-config-org{org_name}.yaml")
        file = open(file_path, "r")
        content = yaml.safe_load(file)
        file.close()

        file = open(file_path, "w")
        content["PeerOrgs"][0]["Template"]["Count"] = count
        yaml.dump(content, file)
        file.close()

