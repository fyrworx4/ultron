import ipaddress

def generate_ip_addresses(user_input):
    # Split the user input into octets
    octets = user_input.split('.')
    
    # Find the octet with the range
    range_octet = None
    for i, octet in enumerate(octets):
        if '-' in octet:
            range_octet = i
            break
    
    ip_addresses = []

    if range_octet:
        
        # Extract the range from the octet
        start, end = map(int, octets[range_octet].split('-'))
        # Generate the IP addresses
        for i in range(start, end + 1):
            octets[range_octet] = str(i)
            ip_address = '.'.join(octets)
            
            # Validate the IP address
            try:
                ipaddress.ip_address(ip_address)
                ip_addresses.append(ip_address)
            except ValueError:
                print(f"Invalid IP address: {ip_address}")

    else:
        ip_address = '.'.join(octets)
        try:
            ipaddress.ip_address(ip_address)
            ip_addresses.append(ip_address)
        except ValueError:
            print(f"Invalid IP address: {ip_address}")

    return ip_addresses


def deal_with_commas(user_input):
    # Split user input into octets
    octets = user_input.split('.')

    # Find the octet with commas
    comma_octet = None
    for i, octet in enumerate(octets):
        if ',' in octet:
            comma_octet = i
            break

    # Split the comma octect into individual numbers
    nums = octets[comma_octet].split(',')
    num_range = range(len(nums))

    # Build the ip address
    ip_addresses = []
    for i in num_range:
        octets[comma_octet] = str(nums[i])
        ip_address = '.'.join(octets)
        ip_addresses.insert(len(ip_addresses), ip_address)

    return ip_addresses
    
def subknit(ip_address):

    ip_addresses = []
    # Separate commas into individual IP range
    if ',' in ip_address:
        ip_addr_with_ranges = deal_with_commas(ip_address)
        for i in range(len(ip_addr_with_ranges)):
            bruh = generate_ip_addresses(ip_addr_with_ranges[i])
            for j in range(len(bruh)):
                ip_addresses.append(bruh[j])
    else:
        ip_addresses = generate_ip_addresses(ip_address)
    

    # Print the IP addresses
    ip_addresses.insert(0, "")
    output = "\n".join(ip_addresses)
    return output


