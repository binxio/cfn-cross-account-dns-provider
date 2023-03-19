# Custom::CrossAccountDNS

The `Custom::CrossAccountDNS` creates Route53 records cross account. You need to host the resource provider in the account has the Route53 host zone. The Custom Resource provider exposes a SNS topic within the organization and/or specific accounts. By allowing the member accounts to publish the Create/Update and Delete actions the custom resource provider will create the records in your Route53 host zone.

## Syntax

```yaml
  DNSRecord:
    Type: Custom::CrossAccountDNS
    Properties:
      ServiceToken: !Sub arn:aws:sns:${AWS::Region}:${HostedZoneAccountId}:binxio-cfn-cross-account-dns-provider
      HostedZoneId: !Ref HostedZoneId
      Name: !Ref DomainName
      Type: CNAME
      Value: !Ref DomainValue
```

## Properties

You can specify the following properties:

    "ServiceToken" - pointing to the function implementing this resource (required).
    "HostedZoneId" - the host zone id in the AWS account hosting the host zone (required).
    "Name" - the name of the record. (required).
    "Type" - to type of the record (required).
    "Value" - the value of the record (required).
    "TTL" - the TTL of the record (optional).
