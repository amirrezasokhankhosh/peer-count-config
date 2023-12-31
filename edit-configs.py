from python_configs.edit_crypto_cfg import edit_crypto_cfg
from python_configs.edit_docker_compose import edit_docker_compose
from python_configs.edit_compose import edit_compose
from python_configs.edit_ccp import edit_ccp
from python_configs.edit_bash import edit_ccp_bash

orgs = [1, 2]
peers = [0, 1]
ports = [7051, 6051, 9051, 8051]

edit_crypto_cfg(orgs=orgs, count=len(peers))
edit_docker_compose(orgs=orgs, peers=peers)
edit_compose(orgs=orgs, peers=peers, ports=ports)
edit_ccp(peers)
edit_ccp_bash(orgs=orgs, peers=peers, ports=ports)