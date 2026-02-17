import boto3
import sys

ebs = boto3.client('ec2')

dry_run = '--dry-run' in sys.argv

try:
    ebs_vol = ebs.describe_volumes()

#print(ebs_vol)


    for volume in ebs_vol.get('Volumes',[]):
        volume_id = volume['VolumeId']
        if volume['State'] == 'available':
            if(dry_run):
                print(f"DRY RUN found available block with VolumeID {volume_id}")
            else:
                try:
                    print(f"Deleting available block with VolumeID {volume_id}")
                    ebs.delete_volume(VolumeId=volume_id)
                    print(f"Deleted block successfully")
                except Exception as e:
                    print(f"Unable to delete the block {volume_id}:{e}")
        else:
            print(f"Volume {volume_id} is in state: {volume['State']}")

except Exception as e:
    print(f"Failed to fetch volumes: {e}")




