import ipaddress

def closest_valid_ip(ip):
    segments = ip.split('.')
    if len(segments) != 4:
        return "192.168.1.1"  # Default fallback IP
    valid_segments = [str(max(0, min(255, int(segment)))) for segment in segments]
    return ".".join(valid_segments)

def closest_valid_subnet_mask(mask):
    try:
        prefix_length = int(mask)
        if prefix_length < 0 or prefix_length > 32:
            raise ValueError
    except ValueError:
        prefix_length = 24  # Default fallback CIDR
    valid_mask = str(ipaddress.IPv4Network((0, prefix_length)).netmask)
    return valid_mask, prefix_length

def calculate_hosts_per_subnet(prefix_length):
    return (2 ** (32 - prefix_length)) - 2

def validate_subnet_mask_or_cidr(value):
    try:
        prefix_length = int(value)
        if 0 <= prefix_length <= 32:
            return True
    except ValueError:
        pass
    try:
        ipaddress.IPv4Network(f"0.0.0.0/{value}")
        return True
    except ValueError:
        return False

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def generate_subnets(base_ip, original_cidr, num_subnets_requested):
    network = ipaddress.ip_network(f'{base_ip}/{original_cidr}', strict=False)
    actual_num_subnets = 2 ** max(1, (num_subnets_requested - 1).bit_length())
    new_prefix_length = original_cidr + (actual_num_subnets - 1).bit_length()

    if new_prefix_length > 32:
        return [], "Requested number of subnets exceeds address space available."

    subnets = list(network.subnets(new_prefix=new_prefix_length))
    explanation = (f"Requested {num_subnets_requested} subnet(s); "
                   f"due to binary subdivision, generated {actual_num_subnets} non-overlapping subnets.")
    return subnets, explanation

def main():
    print("Subnet Helper")
    
    ip_input = input("Enter an IP address: ")
    if not validate_ip(ip_input):
        print(f"Invalid IP address. Suggesting a valid IP closest to {ip_input}...")
        suggested_ip = closest_valid_ip(ip_input)
        print(f"Suggested valid IP: {suggested_ip}")
    else:
        suggested_ip = ip_input

    mask_input = input("Enter a subnet mask or CIDR prefix length: ")
    if not validate_subnet_mask_or_cidr(mask_input):
        print(f"Invalid subnet mask or CIDR. Suggesting a valid subnet mask...")
        mask, prefix_length = closest_valid_subnet_mask(mask_input)
        print(f"Suggested valid subnet mask: {mask} (/{prefix_length} CIDR)")
    else:
        if mask_input.isdigit():
            prefix_length = int(mask_input)
            mask = str(ipaddress.IPv4Network((0, prefix_length)).netmask)
        else:
            mask = mask_input
            prefix_length = ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen

    print(f"Base Network: {suggested_ip}/{prefix_length} with subnet mask {mask}")
    
    try:
        num_subnets_input = int(input("Enter the number of subnets you want to create: "))
        subnets, explanation = generate_subnets(suggested_ip, prefix_length, num_subnets_input)
        
        if not subnets:
            print("Could not generate subnets with the given input.")
        else:
            print(explanation)  # Display the explanation to the user
            print(f"Suggested non-overlapping CIDRs for {num_subnets_input} subnets:")
            for subnet in subnets:
                print(subnet)
    except ValueError:
        print("Invalid input. Please ensure you enter a numerical value for the number of subnets.")

if __name__ == "__main__":
    main()
