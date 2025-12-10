# EKS Secure VPC Infrastructure

This directory contains the Pulumi configuration for a secure VPC infrastructure designed to host an Amazon EKS cluster that meets CMMC, CIS, and GDPR compliance standards.

## Overview

This infrastructure creates a highly available, secure VPC suitable for hosting EKS workloads that handle GDPR-regulated data and meet CMMC and CIS security benchmarks.

## Architecture

### Network Configuration

- **VPC CIDR**: `10.100.0.0/16`
- **Region**: `us-east-1` (single region deployment)
- **Availability Zones**: 3 AZs (`us-east-1a`, `us-east-1b`, `us-east-1c`)

### Subnets

**Public Subnets** (for load balancers and NAT Gateways):
- `10.100.1.0/24` - us-east-1a
- `10.100.2.0/24` - us-east-1b
- `10.100.3.0/24` - us-east-1c

**Private Subnets** (for EKS worker nodes and pods):
- `10.100.11.0/24` - us-east-1a
- `10.100.12.0/24` - us-east-1b
- `10.100.13.0/24` - us-east-1c

## Compliance Features

### CMMC (Cybersecurity Maturity Model Certification)

- **Network Segmentation**: Public and private subnets provide clear separation between internet-facing and internal resources
- **Controlled Access**: NAT Gateways provide controlled outbound internet access from private subnets
- **High Availability**: Multi-AZ deployment ensures resilience
- **Tagging**: Comprehensive tagging for asset tracking and management

### CIS AWS Foundations Benchmark

- **Network Isolation**: Private subnets for workload isolation
- **NAT Gateways**: Enabled for secure outbound connectivity from private subnets (one per AZ)
- **Internet Gateway**: Dedicated for public subnet internet access
- **DNS Support**: Enabled for proper name resolution
- **Multiple AZs**: Three availability zones for fault tolerance

### GDPR (General Data Protection Regulation)

- **Data Classification Tags**: Resources tagged with `data-classification: gdpr-capable`
- **Network Isolation**: Private subnets ensure data processing happens in isolated network segments
- **Audit Trail**: Tags include creation metadata for accountability
- **Region Control**: Single-region deployment to maintain data residency requirements

## Security Best Practices

1. **Private Workloads**: EKS worker nodes should be deployed in private subnets
2. **NAT Gateway**: Enabled for private subnet outbound connectivity without direct internet exposure
3. **Security Groups**: Default security group created (should be customized per workload)
4. **Network Segmentation**: Clear separation between public and private subnets

## Outputs

The following outputs are available after deployment:

- `vpc_id`: VPC identifier
- `vpc_arn`: VPC ARN for IAM policies
- `public_subnet_ids`: List of public subnet IDs (for load balancers)
- `private_subnet_ids`: List of private subnet IDs (for EKS nodes)
- `internet_gateway_id`: Internet Gateway identifier
- `nat_gateway_ids`: NAT Gateway identifiers (one per AZ)
- `default_security_group_id`: Default security group ID

## Deployment

### Prerequisites

1. AWS credentials configured with appropriate permissions
2. Pulumi CLI installed
3. S3 backend for Pulumi state configured

### Deploy

```bash
cd pulumi/environments/aws/staging/001-eks-secure
pulumi login s3://your-pulumi-backend/staging
pulumi stack select organization/eks-secure-vpc/staging
pulumi preview  # Review changes
pulumi up       # Apply changes
```

### Testing in PR

This configuration uses a local component reference (`@0.0.0`) for development and testing. When changes are merged to main:

1. Create a GitHub release for the VPC component
2. Update `Pulumi.yaml` to reference the release version
3. Update the SDK file in `sdks/vpc/` to match the new version

## Future Enhancements

For a production-ready EKS cluster, consider adding:

1. **VPC Flow Logs**: Enable for network traffic monitoring and compliance auditing
2. **Additional Security Groups**: Create specific security groups for EKS control plane and worker nodes
3. **Network ACLs**: Add network ACLs for additional subnet-level security
4. **VPC Endpoints**: Add AWS service endpoints to keep traffic within the AWS network
5. **KMS Encryption**: Configure KMS keys for encrypting sensitive data
6. **Transit Gateway**: For multi-VPC connectivity if needed
7. **AWS Network Firewall**: For advanced threat protection and filtering

## Tags

All resources are tagged with:
- `environment: staging`
- `compliance: CMMC,CIS,GDPR`
- `purpose: eks-cluster`
- `data-classification: gdpr-capable`
- `created_by: pulumi`
- `github_repository: devops-with-ai`
- `github_repository_path: pulumi/environments/aws/staging/001-eks-secure`

## References

- [CMMC Compliance](https://www.acq.osd.mil/cmmc/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [GDPR Overview](https://gdpr.eu/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
