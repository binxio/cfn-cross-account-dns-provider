from __future__ import annotations
from typing import Any, Dict, List
import boto3
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider, SnsEnvelope
import logging
from os import getenv

logger = logging.getLogger()
client = boto3.client("route53")
logging.basicConfig(level=getenv("LOG_LEVEL", "INFO"))


request_schema = {
    "type": "object",
    "required": ["HostedZoneId", "Name", "Type", "Value"],
    "additionalProperties": True,
    "properties": {
        "HostedZoneId": {
            "type": "string",
            "description": "The Id of the host zone that we needs to be updated.",
        },
        "Name": {"type": "string", "description": "The name of the DNS record"},
        "Type": {"type": "string", "description": "The type of the DNS record"},
        "Value": {
            "type": "string",
            "description": "The value used to set the DNS record",
        },
        "TTL": {
            "type": "number",
            "description": "The TTL that will be set on the DNS record.",
        },
    },
}


class CrossAccountDNSProvider(ResourceProvider):
    """
    A Custom Cross Account DNS Provider to provide the ability manage DNS records cross account
    """

    def __init__(self):
        super(CrossAccountDNSProvider, self).__init__()
        self.request_schema = request_schema

    @property
    def hosted_zone_id(self) -> str:
        return self.get("HostedZoneId", "")

    @property
    def name(self) -> str:
        return self.get("Name", "")

    @property
    def type(self) -> str:
        return self.get("Type", "")

    @property
    def value(self) -> str:
        return self.get("Value", "")

    @property
    def ttl(self) -> int:
        return int(self.get("TTL", 900))

    def __render_cloudfront_alias(self) -> Dict[str, Any]:
        return {
            "Name": self.name,
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z2FDTNDATAQYW2",
                "DNSName": self.value,
                "EvaluateTargetHealth": False,
            },
        }

    @property
    def record_set(self) -> Dict[str, Any]:
        if self.value.endswith(".cloudfront.net"):
            data = self.__render_cloudfront_alias()
            return data

        return {
            "Name": self.name,
            "Type": self.type,
            "TTL": self.ttl,
            "ResourceRecords": [{"Value": self.value}],
        }

    def create(self):
        logger.info(f"Create {self.name} record")
        client.change_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            ChangeBatch={
                "Changes": [{"Action": "CREATE", "ResourceRecordSet": self.record_set}]
            },
        )
        self.physical_resource_id = self.name

        # InvalidChangeBatch: An error occurred (InvalidChangeBatch) when calling the ChangeResourceRecordSets operation:
        # [RRSet with DNS name _f053acec0ecafbe37a60c70ac62dc6a7.www.development.stonesculpture.nl. is not permitted in zone conijn.io.]

    def update(self):
        logger.info(f"Update {self.physical_resource_id} record")
        if self.old_properties and self.properties != self.old_properties:
            client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch={
                    "Changes": [
                        {"Action": "UPSERT", "ResourceRecordSet": self.record_set}
                    ]
                },
            )

            if self.name != self.get_old("Name", self.name):
                # When the name changes we need to trigger a replacement
                self.physical_resource_id = self.name

        else:
            self.success("nothing to change")

    def delete(self):
        logger.info(f"Delete {self.physical_resource_id} record")

        try:
            client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch={
                    "Changes": [
                        {"Action": "DELETE", "ResourceRecordSet": self.record_set}
                    ]
                },
            )
        except ClientError as error:
            # An error occurred (InvalidChangeBatch) when calling the ChangeResourceRecordSets operation:
            # [Tried to delete resource record set [name='development.stonesculpture.nl.', type='A'] but it was not found]
            self.success(f"Ignore failure to delete record: {error}")


def handler(event: dict, context: Any) -> List[dict]:
    provider = SnsEnvelope(resource_provider=CrossAccountDNSProvider)
    return provider.handle(event, context)
