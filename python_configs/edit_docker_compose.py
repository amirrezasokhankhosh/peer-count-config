import yaml
import os


cwd = os.path.dirname(__file__)
cli = {'container_name': 'cli', 
       'image': 'hyperledger/fabric-tools:latest', 
       'volumes': ['./docker/peercfg:/etc/hyperledger/peercfg']}
docker_compose_path = os.path.abspath(os.path.join(cwd, "../test-network/compose/docker/docker-compose-test-net.yaml"))


def edit_services(orgs, peers):
    res = {}
    for org_num in orgs:
        for peer_num in peers:
            temp = {'container_name': f'peer{peer_num}.org{org_num}.example.com', 
                    'image': 'hyperledger/fabric-peer:latest', 
                    'labels': {'service': 'hyperledger-fabric'}, 
                    'environment': ['CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock', 
                                    'CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=fabric_test'], 
                    'volumes': ['./docker/peercfg:/etc/hyperledger/peercfg', 
                                '${DOCKER_SOCK}:/host/var/run/docker.sock']}
            res[f'peer{peer_num}.org{org_num}.example.com'] = temp

    res["cli"] = cli
    return res


def edit_docker_compose(orgs, peers):
    file = open(docker_compose_path, "r")
    content = yaml.safe_load(file)
    file.close()

    content["services"] = edit_services(orgs, peers)
    file = open(docker_compose_path, "w")
    yaml.dump(content, file)
    file.close()