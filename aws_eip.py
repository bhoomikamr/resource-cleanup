import boto3
import sys

# Dry run check
dry_run = '--dry-run' in sys.argv

ec2 = boto3.client('ec2')

try:
    eip_addr = ec2.describe_addresses()
    
    for eip in eip_addr.get("Addresses", []):
        public_ip = eip['PublicIp']
        
        if 'AssociationId' not in eip:
            if dry_run:
                print(f"DRY RUN Found unallocated IP {public_ip}")
            else:
                try:
                    print(f" Releasing {public_ip}...")
                    ec2.release_address(AllocationId=eip['AllocationId'])
                    print(f"{public_ip} released successfully.")
                except Exception as e:
                    print(f"Could not release {public_ip}: {e}")
        else:
            instance_id = eip.get('InstanceId', 'Unknown')
            print(f"IP {public_ip} is allocated with Instance: {instance_id}")

except Exception as e:
    print(f"Failed to fetch addresses: {e}")