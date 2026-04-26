import boto3
import sys

dry_run = '--dry-run' in sys.argv

ec2 = boto3.client('ec2')


snapshots = ec2.describe_snapshots(OwnerIds=['self'])

#print(snapshots)

for snapshot in snapshots.get('Snapshots',[]):
    if 'Created by CreateImage' in snapshot.get('Description',''):
        print(f"Snapshot {snapshot['SnapshotId']} cannot be deleted as it is linked to an AMI")
    else:
        try:
            ec2.describe_volumes(VolumeIds=[snapshot['VolumeId']])
            print(f"Snapshot {snapshot['SnapshotId']} cannot be deleted as its volume {snapshot['VolumeId']} still exists")
        except Exception as e:
            #print(f"Exception:{e}")
            if 'InvalidVolume.NotFound' in str(e):
                if dry_run:    
                    print(f"DRY RUN will delete snapshot {snapshot['SnapshotId']} with unattached volume")
                else:
                    print(f"Deleting snapshot {snapshot['SnapshotId']}")
                    ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                    print(f"Snapshot deleted successfully")





    
     
