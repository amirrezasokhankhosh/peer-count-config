import os

cwd = os.path.dirname(__file__)
text = r"""
#!/bin/bash

function one_line_pem {
    echo "`awk 'NF {sub(/\\n/, ""); printf "%s\\\\\\\n",$0;}' $1`"
}

"""

def add_body(peers):
    num_inputs = 4 + len(peers)
    body = ""
    body += f"\tlocal PP=$(one_line_pem ${num_inputs - 1})\n"
    body += f"\tlocal CP=$(one_line_pem ${num_inputs})\n"
    body += f"\tsed -e \"s/\${{ORG}}/$1/\" \\\n"
    for i in range(2, num_inputs - 2):
        body += f"\t\t-e \"s/\${{P{i-2}PORT}}/${i}/\" \\\n"
    body += f"\t\t-e \"s/\${{CAPORT}}/${num_inputs - 2}/\" \\\n"
    body += "\t\t-e \"s#\${PEERPEM}#$PP#\" \\\n"
    body += "\t\t-e \"s#\${CAPEM}#$CP#\" \\\n"
    return body.expandtabs(4)

def add_functions(peers):
    body = add_body(peers)
    functions = "function json_ccp {\n"
    functions += body
    functions += "\t\torganizations/ccp-template.json\n}\n\n".expandtabs(4)
    functions += "function yaml_ccp {\n"
    functions += body
    functions += "\t\t".expandtabs(4) + r"organizations/ccp-template.yaml | sed -e $'s/\\\\n/\\\n          /g'"
    functions += "\n}\n\n"
    return functions

def add_cfgs(orgs, peers, ports):
    cfgs = ""
    for i in range(len(orgs)):
        cfgs += f"ORG={orgs[i]}\n"
        for j in range(len(peers)):
            cfgs += f"P{peers[j]}PORT={ports[i*len(peers) + j]}\n"
        cfgs += f"CAPORT={ports[i*len(peers)]+3}\n"
        cfgs += f"PEERPEM=organizations/peerOrganizations/org{orgs[i]}.example.com/tlsca/tlsca.org{orgs[i]}.example.com-cert.pem\n"
        cfgs += f"CAPEM=organizations/peerOrganizations/org{orgs[i]}.example.com/ca/ca.org{orgs[i]}.example.com-cert.pem\n\n"
        cfgs += "echo \"$(json_ccp $ORG "
        for j in range(len(peers)):
            cfgs += f"$P{j}PORT "
        cfgs += f"$CAPORT $PEERPEM $CAPEM)\" > organizations/peerOrganizations/org{orgs[i]}.example.com/connection-org{orgs[i]}.json\n"
        cfgs += "echo \"$(yaml_ccp $ORG "
        for j in range(len(peers)):
            cfgs += f"$P{j}PORT "
        cfgs += f"$CAPORT $PEERPEM $CAPEM)\" > organizations/peerOrganizations/org{orgs[i]}.example.com/connection-org{orgs[i]}.yaml\n\n"
    return cfgs

def add_sh(orgs, peers, ports):
    global text
    text += add_functions(peers)
    text += add_cfgs(orgs, peers, ports)

def edit_ccp_bash(orgs, peers, ports):
    add_sh(orgs, peers, ports)
    bash_path = os.path.abspath(os.path.join(cwd, "../test-network/organizations/ccp-generate.sh"))
    file = open(bash_path, 'w')
    file.write(text)
    file.close()