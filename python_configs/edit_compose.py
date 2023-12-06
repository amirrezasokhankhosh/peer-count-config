import yaml
import os

cwd = os.path.dirname(__file__)
compose_path = os.path.abspath(os.path.join(cwd, "../test-network/compose/compose-test-net.yaml"))
global_port = 9443

orderer = {'container_name': 'orderer.example.com', 
           'image': 'hyperledger/fabric-orderer:latest', 
           'labels': {'service': 'hyperledger-fabric'}, 
           'environment': ['FABRIC_LOGGING_SPEC=INFO', 
                           'ORDERER_GENERAL_LISTENADDRESS=0.0.0.0', 
                           'ORDERER_GENERAL_LISTENPORT=7050', 
                           'ORDERER_GENERAL_LOCALMSPID=OrdererMSP', 
                           'ORDERER_GENERAL_LOCALMSPDIR=/var/hyperledger/orderer/msp', 
                           'ORDERER_GENERAL_TLS_ENABLED=true', 
                           'ORDERER_GENERAL_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key', 
                           'ORDERER_GENERAL_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt', 
                           'ORDERER_GENERAL_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]', 
                           'ORDERER_GENERAL_CLUSTER_CLIENTCERTIFICATE=/var/hyperledger/orderer/tls/server.crt', 
                           'ORDERER_GENERAL_CLUSTER_CLIENTPRIVATEKEY=/var/hyperledger/orderer/tls/server.key', 
                           'ORDERER_GENERAL_CLUSTER_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]', 
                           'ORDERER_GENERAL_BOOTSTRAPMETHOD=none', 
                           'ORDERER_CHANNELPARTICIPATION_ENABLED=true', 
                           'ORDERER_ADMIN_TLS_ENABLED=true', 
                           'ORDERER_ADMIN_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt', 
                           'ORDERER_ADMIN_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key', 
                           'ORDERER_ADMIN_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]', 
                           'ORDERER_ADMIN_TLS_CLIENTROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]', 
                           'ORDERER_ADMIN_LISTENADDRESS=0.0.0.0:7053', 
                           f'ORDERER_OPERATIONS_LISTENADDRESS=orderer.example.com:{global_port}', 
                           'ORDERER_METRICS_PROVIDER=prometheus'], 
            'working_dir': '/root', 
            'command': 'orderer', 
            'volumes': ['../organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp:/var/hyperledger/orderer/msp', 
                        '../organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/:/var/hyperledger/orderer/tls', 
                        'orderer.example.com:/var/hyperledger/production/orderer'], 
            'ports': ['7050:7050', 
                      '7053:7053', 
                      f'{global_port}:{global_port}'], 
            'networks': ['test']
}
cli = {
    'container_name': 'cli', 
    'image': 'hyperledger/fabric-tools:latest', 
    'labels': {'service': 'hyperledger-fabric'}, 
    'tty': True, 
    'stdin_open': True, 
    'environment': ['GOPATH=/opt/gopath', 
                    'FABRIC_LOGGING_SPEC=INFO', 
                    'FABRIC_CFG_PATH=/etc/hyperledger/peercfg'], 
    'working_dir': '/opt/gopath/src/github.com/hyperledger/fabric/peer', 
    'command': '/bin/bash', 
    'volumes': [
        '../organizations:/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations', 
        '../scripts:/opt/gopath/src/github.com/hyperledger/fabric/peer/scripts/'], 
    'depends_on': [], 
    'networks': ['test']}

def edit_volumes(orgs, peers):
    volumes = {}
    for org_num in orgs:
        for peer_num in peers:
            volumes[f"peer{peer_num}.org{org_num}.example.com"] = None
    volumes["orderer.example.com"] = None
    return volumes

def edit_services(orgs, peers, ports):
    global global_port
    services = {}
    for i in range(len(orgs)):
        for j in range(len(peers)):
            port = ports[i*len(peers) + j]
            org_num = orgs[i]
            peer_num = peers[j]
            global_port += 1
            cfg = {'container_name': f'peer{peer_num}.org{org_num}.example.com', 
                   'image': 'hyperledger/fabric-peer:latest', 
                   'labels': {'service': 'hyperledger-fabric'}, 
                   'environment': ['FABRIC_CFG_PATH=/etc/hyperledger/peercfg', 
                                   'FABRIC_LOGGING_SPEC=INFO', 
                                   'CORE_PEER_TLS_ENABLED=true', 
                                   'CORE_PEER_PROFILE_ENABLED=false', 
                                   'CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt', 
                                   'CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key', 
                                   'CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt', 
                                   f'CORE_PEER_ID=peer{peer_num}.org{org_num}.example.com', 
                                   f'CORE_PEER_ADDRESS=peer{peer_num}.org{org_num}.example.com', 
                                   f'CORE_PEER_LISTENADDRESS=0.0.0.0:{port}', 
                                   f'CORE_PEER_CHAINCODEADDRESS=peer{peer_num}.org{org_num}.example.com:{port+1}', 
                                   f'CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:{port+1}', 
                                   f'CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer{peer_num}.org{org_num}.example.com:{port}', 
                                   f'CORE_PEER_GOSSIP_BOOTSTRAP=peer{peer_num}.org{org_num}.example.com:{port}', 
                                   f'CORE_PEER_LOCALMSPID=Org{org_num}MSP', 
                                   'CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/fabric/msp', 
                                   f'CORE_OPERATIONS_LISTENADDRESS=peer{peer_num}.org{org_num}.example.com:{global_port}', 
                                   'CORE_METRICS_PROVIDER=prometheus', 
                                   f'CHAINCODE_AS_A_SERVICE_BUILDER_CONFIG={{"peername":"peer{peer_num}org{org_num}"}}', 
                                   'CORE_CHAINCODE_EXECUTETIMEOUT=300s'], 
                    'volumes': [f'../organizations/peerOrganizations/org{org_num}.example.com/peers/peer{peer_num}.org{org_num}.example.com:/etc/hyperledger/fabric', 
                                f'peer{peer_num}.org{org_num}.example.com:/var/hyperledger/production'], 
                    'working_dir': '/root', 
                    'command': 'peer node start', 
                    'ports': [f'{port}:{port}', 
                              f'{global_port}:{global_port}'], 
                    'networks': ['test']
            }
            services[f"peer{peer_num}.org{org_num}.example.com"] = cfg
            cli["depends_on"].append(f"peer{peer_num}.org{org_num}.example.com")
    services["cli"] = cli
    services["orderer.example.com"] = orderer
    return services

def edit_compose(orgs, peers, ports):
    file = open(compose_path, 'r')
    content = yaml.safe_load(file)
    file.close()

    content["volumes"] = edit_volumes(orgs, peers)
    content["services"] = edit_services(orgs, peers, ports)
    file = open(compose_path, 'w')
    yaml.dump(content, file)
    file.close()