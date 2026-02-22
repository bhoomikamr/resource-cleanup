import boto3
import os

def lambda_handler(event, context):
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # Get all available regions
    global_ec2 = boto3.client('ec2')
    regions = [r['RegionName'] for r in global_ec2.describe_regions()['Regions']]

    for region in regions:
        print(f"--- Checking Region: {region} ---")
        ec2 = boto3.client('ec2', region_name=region)

        # 1. EIP cleanup
        try:
            eip_addr = ec2.describe_addresses()
            for eip in eip_addr.get("Addresses", []):
                public_ip = eip['PublicIp']
                
                # Tag Check
                tags = eip.get('Tags', [])
                if any(t['Key'].lower() == 'keep' for t in tags):
                    continue

                if 'AssociationId' not in eip:
                    if dry_run:
                        print(f"[{region}] DRY RUN Found unallocated IP {public_ip}")
                    else:
                        try:
                            ec2.release_address(AllocationId=eip['AllocationId'])
                            print(f"[{region}] Released {public_ip}")
                        except Exception as e:
                            print(f"Error releasing {public_ip}: {e}")
        except Exception as e:
            print(f"Failed EIPs in {region}: {e}")

        # 2. EBS cleanup
        try:
            ebs_vol = ec2.describe_volumes()
            for volume in ebs_vol.get('Volumes', []):
                volume_id = volume['VolumeId']
                
                # Tag Check
                tags = volume.get('Tags', [])
                if any(t['Key'].lower() == 'keep' for t in tags):
                    continue

                if volume['State'] == 'available':
                    if dry_run:
                        print(f"[{region}] DRY RUN Found available volume {volume_id}")
                    else:
                        try:
                            ec2.delete_volume(VolumeId=volume_id)
                            print(f"[{region}] Deleted volume {volume_id}")
                        except Exception as e:
                            print(f"Error deleting volume {volume_id}: {e}")
        except Exception as e:
            print(f"Failed volumes in {region}: {e}")

        # 3. EBS Snapshot cleanup
        try:
            snapshots = ec2.describe_snapshots(OwnerIds=['self'])
            for snapshot in snapshots.get('Snapshots', []):
                snap_id = snapshot['SnapshotId']

                # Tag Check
                tags = snapshot.get('Tags', [])
                if any(t['Key'].lower() == 'keep' for t in tags):
                    continue

                if 'Created by CreateImage' in snapshot.get('Description', ''):
                    continue
                else:
                    try:
                        ec2.describe_volumes(VolumeIds=[snapshot['VolumeId']])
                    except Exception as e:
                        if 'InvalidVolume.NotFound' in str(e):
                            if dry_run:
                                print(f"[{region}] DRY RUN Found orphan snapshot {snap_id}")
                            else:
                                ec2.delete_snapshot(SnapshotId=snap_id)
                                print(f"[{region}] Deleted snapshot {snap_id}")
        except Exception as e:
            print(f"Failed snapshots in {region}: {e}")

    return {'statusCode': 200, 'body': 'Global cleanup finished'}