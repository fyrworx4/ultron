import ipaddress
import subprocess
import random
import sys
from pythonping import ping

def get_network_info():
    
    interface = subprocess.check_output("ip route | grep default | awk '{print $5}'", shell=True, text=True).strip()
    ip_cidr = subprocess.check_output(f"ip -o -f inet addr show | grep {interface} | awk '/scope global/ {print $4}'", shell=True, text=True).split("/")
    default_gateway = subprocess.check_output("route -n | grep 'UG[ \\t]' | awk '{print $2}'", shell=True, text=True).strip()
    netmask = ip_cidr[1].strip()

    return {
        "ip_cidr": ip_cidr,
        "default_gateway": default_gateway,
        "interface": interface,
        "netmask": netmask
    }

def get_host_bits(ip_with_cidr):
    # Parse the IP address with CIDR notation
    network = ipaddress.IPv4Network(ip_with_cidr, strict=False)
    
    # Get the prefix length (number of network bits)
    prefix_length = network.prefixlen
    
    # IPv4 has 32 bits total, so host bits are 32 minus prefix length
    host_bits = 32 - prefix_length
    
    # Calculate number of available hosts (2^host_bits - 2)
    # We subtract 2 for the network address and broadcast address
    available_hosts = 2 ** host_bits - 2
    
    return {
        'host_bits': host_bits,
        'available_hosts': available_hosts,
        'network_address': str(network.network_address),
        'broadcast_address': str(network.broadcast_address),
        'netmask': str(network.netmask)
    }

def generate_random_ip_upper_third(network_address, broadcast_address, netmask):
    network_octets = [int(x) for x in network_address.split(".")]
    broadcast_octets = [int(x) for x in broadcast_address.split(".")]
    
    # Calculate total host address space size
    # First convert to 32-bit integers
    network_int = (network_octets[0] << 24) + (network_octets[1] << 16) + (network_octets[2] << 8) + network_octets[3]
    broadcast_int = (broadcast_octets[0] << 24) + (broadcast_octets[1] << 16) + (broadcast_octets[2] << 8) + broadcast_octets[3]
    
    # Calculate range size (excluding network and broadcast if applicable)
    if netmask < 31:  # Normal subnets: exclude network and broadcast
        total_hosts = broadcast_int - network_int - 1
        start_host = network_int + 1
    else:  # /31 and /32 have special handling
        total_hosts = broadcast_int - network_int + 1
        start_host = network_int
    
    # Calculate where the upper third begins
    upper_third_start = start_host + (total_hosts * 2 // 3)
    
    # Generate a random IP in the upper third
    random_ip_int = random.randint(upper_third_start, broadcast_int - (1 if netmask < 31 else 0))
    
    # Convert back to dotted format
    random_ip_octets = [
        (random_ip_int >> 24) & 0xFF,
        (random_ip_int >> 16) & 0xFF,
        (random_ip_int >> 8) & 0xFF,
        random_ip_int & 0xFF
    ]
    
    return ".".join(str(octet) for octet in random_ip_octets)


def switch_ip(new_ip, default_gateway, interface, cidr):
    # check if IP address already exists on the network
    print(f"[i] Checking if {new_ip} exists on the network...")
    ping_results = ping(new_ip, timeout=2, count=3)
    
    results_list = []
    for results in ping_results:
        results_list.append(results.message)

    # if the IP address is free to taking, let's take it
    if (all(i == None for i in results_list)):
        subprocess.check_output(f"ip address flush dev {interface}", shell=True)
        subprocess.check_output(f"ip route flush dev {interface}", shell=True)
        subprocess.check_output(f"ip address add {new_ip}/{cidr} brd + dev {interface}", shell=True)
        subprocess.check_output(f"ip route add {default_gateway} dev {interface}", shell=True)
        subprocess.check_output(f"ip route add default via {default_gateway} dev {interface}", shell=True)

        print(f"[+] New IP: {new_ip}")
        return new_ip
    else:
        print(f"[!] Error! {new_ip} already exists on the network") 


if __name__ == "__main__":
    channel_id = sys.argv[1]

    network_info = get_network_info()
    result = get_host_bits("/".join(network_info["ip_cidr"]).strip())
    
    while True:
        # generate a random IP in the higher range
        new_ip = generate_random_ip_upper_third(result["network_address"], result["broadcast_address"], int(network_info["netmask"]))

        # attempt to switch the IP
        confirmed_new_ip = switch_ip(new_ip, network_info["default_gateway"], network_info["interface"], network_info["netmask"])

        # Write the channel ID and new IP to a file so we can access it after reconnection
        with open("ip_change_info.txt", "w") as f:
            f.write(f"{channel_id}\n{new_ip}")

        if confirmed_new_ip:
            break
        

    subprocess.Popen(["python3", "ultron2.py"])
