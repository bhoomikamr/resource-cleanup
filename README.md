# AWS Resource Cleanup Automation

## Overview

This project automates the cleanup of unused AWS resources across all AWS regions to help reduce unnecessary cloud costs.

The solution identifies and optionally removes:

- Unused Elastic IP addresses
- Unattached EBS volumes
- Orphaned EBS snapshots

The project was developed incrementally, starting with standalone Python cleanup scripts and later consolidated into a centralized AWS Lambda solution deployed with Terraform, with `lambda_function.py` serving as the primary entry point.

---

## Features

### Elastic IP Cleanup
Identifies and optionally removes:
- Allocated but unassociated Elastic IPs
- Idle public IP addresses that incur AWS charges

### EBS Volume Cleanup
Identifies and optionally removes:
- Volumes in `available` state
- Unattached EBS storage volumes

### Snapshot Cleanup
Identifies and optionally removes:
- Snapshots not linked to any existing EBS volume
- Old orphaned snapshots

### Safety Features
Includes:
- `DRY_RUN` mode for safe testing
- Tag-based exclusion using:

```bash
Key: `Keep`
Value: `true`
```
Resources with a Keep tag will not be deleted.

## Multi-Region Support

Automatically scans:

- All AWS regions in the account
- Performs cleanup region by region

## Architecture

```text
EventBridge (Weekly Schedule)
        ↓
AWS Lambda Function
        ↓
Boto3 Cleanup Engine
        ↓
Cleanup AWS Resources
```
## Project Structure

```bash
resource-cleanup/
│── README.md
│── aws_eip.py
│── ebs_cleanup.py
│── ebs_snapshots.py
│── lambda_function.py
│── lambda_cleanup.tf
│── lambda_function.zip
```
## Technologies Used

- Python
- Boto3
- AWS Lambda
- Amazon EventBridge
- CloudWatch Logs
- Terraform

## IAM Permissions Used

The Lambda function requires permissions for:

- `ec2:DescribeRegions`
- `ec2:DescribeAddresses`
- `ec2:ReleaseAddress`
- `ec2:DescribeVolumes`
- `ec2:DeleteVolume`
- `ec2:DescribeSnapshots`
- `ec2:DeleteSnapshot`
- CloudWatch logging permissions

## Deployment with Terraform

### Initialize Terraform
```bash
terraform init
```
### Review changes
```bash
terraform plan
```
### Deploy resources
```bash
terraform apply
```
### Terraform creates:

- Lambda execution role
- IAM policy
- Lambda function
- EventBridge schedule rule
- CloudWatch integration

## Lambda Environment Variable
```bash
DRY_RUN=true
```
## Values

| Value | Behavior |
|-------|----------|
| true  | Only logs resources |
| false | Deletes resources   |

## Running Individual Scripts

### EIP cleanup
```bash
python aws_eip.py --dry-run
```
### EBS cleanup
```bash
python ebs_cleanup.py --dry-run
```
### Snapshot cleanup
```bash
python ebs_snapshots.py --dry-run
```
## Example Output
```bash
--- Checking Region: us-east-1 ---
[us-east-1] DRY RUN Found unallocated IP 54.x.x.x
[us-east-1] DRY RUN Found available volume vol-0123456789
[us-east-1] DRY RUN Found orphan snapshot snap-0123456789
```
## Resource Protection

To prevent accidental deletion, add this tag:
```bash
Key: Keep
Value: true
```
Tagged resources are skipped automatically.

## Schedule

Cleanup runs weekly using EventBridge:
```bash
cron(0 0 ? * MON *)
```
Runs every Monday at 00:00 UTC.

## Benefits

This project helps:

- Reduce AWS monthly costs
- Remove forgotten resources
- Automate routine maintenance
- Improve operational efficiency

## Future Improvements

Possible enhancements:

- SNS email alerts
- Slack notifications
- Resource age filtering
- Cost reporting
- Cross-account cleanup
