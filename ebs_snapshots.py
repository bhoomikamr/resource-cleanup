import boto3
import sys

dry_run = '--dry-run' in sys.argv

ec2 = boto3.client('ec2')


snapshots = ec2.describe_snapshots(OwnerIds=['self'])

print(snapshots)

for snapshot in snapshots.get('Snapshots',[]):
    if 'Created by CreateImage' in snapshot.get('Description',''):
        print(f"Snapshot {snapshot['SnapshotId']} cannot be deleted as it is linked to an AMI")




    
     
