from __future__ import annotations
import json
from typing import List, Optional
from datetime import datetime
import uuid


class SnsWrapper(dict):
    def __init__(self, requests: List[Request]) -> None:
        messages = map(json.dumps, requests)
        self.update({
            "Records": list(map(lambda message: {"Sns": {"Message": message}}, messages))
        })


class RequestProperties(dict):
    def __init__(self, request_type: str, properties: dict) -> None:
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://mocked-url.com/path",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": "request-%s" % uuid.uuid4(),
                "ResourceType": "Custom::CrossAccountDNS",
                "LogicalResourceId": "Record",
                "ResourceProperties": properties,
            }
        )


class Request(RequestProperties):
    def __init__(
        self,
        request_type: str,
        name: str,
        type: str,
        value: str,
        ttl: Optional[int] = None,
        physical_resource_id: Optional[str] = None,
    ):
        super().__init__(
            request_type,
            {
                "HostedZoneId": "MYHOSTZONE_ID",
                "Name": name,
                "Type": type,
                "Value": value,
            },
        )

        if ttl:
            self["ResourceProperties"]["TTL"] = ttl

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id


class Route53Request(dict):
    def __init__(
        self,
        action: str,
        name: str,
        type: str,
        value: Optional[str] = None,
        alias_target: Optional[dict] = None,
        ttl: Optional[int] = 900,
    ):
        record_set = {
            "Name": name,
            "Type": type,
        }

        if alias_target:
            record_set["AliasTarget"] = alias_target
        else:
            if ttl:
                record_set["TTL"] = ttl
            record_set["ResourceRecords"] = [{"Value": value}]

        self.update(
            {
                "HostedZoneId": "MYHOSTZONE_ID",
                "ChangeBatch": {
                    "Changes": [{"Action": action, "ResourceRecordSet": record_set}]
                },
            }
        )


class Route53Response(dict):
    def __init__(self) -> None:
        self.update(
            {
                "ChangeInfo": {
                    "Id": str(uuid.uuid4()),
                    "Status": "INSYNC",
                    "SubmittedAt": datetime.utcnow(),
                }
            }
        )
