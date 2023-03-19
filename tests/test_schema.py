import cfn_resource_provider
from unittest.mock import patch
import pytest
from cfn_cross_account_dns_provider.cross_account_dns import CrossAccountDNSProvider, client
from tests.shared_resources import RequestProperties


@pytest.mark.parametrize(
    "event,reason",
    [
        pytest.param(
            RequestProperties("Create", {}),
            "invalid resource properties",
            id="no-properties",
        ),
        pytest.param(
            RequestProperties("Create", {"Name": "Foo", "Type": "Foo", "Value": "Foo"}),
            "invalid resource properties",
            id="no-host-zone-id",
        ),
        pytest.param(
            RequestProperties(
                "Create", {"HostedZoneId": "Foo", "Type": "Foo", "Value": "Foo"}
            ),
            "invalid resource properties",
            id="no-name",
        ),
        pytest.param(
            RequestProperties(
                "Create", {"HostedZoneId": "Foo", "Name": "Foo", "Value": "Foo"}
            ),
            "invalid resource properties",
            id="no-type",
        ),
        pytest.param(
            RequestProperties(
                "Create", {"HostedZoneId": "Foo", "Name": "Foo", "Type": "Foo"}
            ),
            "invalid resource properties",
            id="no-value",
        ),
        pytest.param(
            RequestProperties(
                "Create",
                {"HostedZoneId": 1, "Name": "Foo", "Type": "Foo", "Value": "Foo"},
            ),
            "invalid resource properties",
            id="invalid-host-zone-id",
        ),
        pytest.param(
            RequestProperties(
                "Create",
                {"HostedZoneId": "Foo", "Name": 1, "Type": "Foo", "Value": "Foo"},
            ),
            "invalid resource properties",
            id="invalid-name",
        ),
        pytest.param(
            RequestProperties(
                "Create",
                {"HostedZoneId": "Foo", "Name": "Foo", "Type": 1, "Value": "Foo"},
            ),
            "invalid resource properties",
            id="invalid-type",
        ),
        pytest.param(
            RequestProperties(
                "Create",
                {"HostedZoneId": "Foo", "Name": "Foo", "Type": "Foo", "Value": 1},
            ),
            "invalid resource properties",
            id="invalid-value",
        ),
        pytest.param(
            RequestProperties(
                "Create",
                {
                    "HostedZoneId": "Foo",
                    "Name": "Foo",
                    "Type": "Foo",
                    "Value": "Foo",
                    "TTL": "1",
                },
            ),
            "invalid resource properties",
            id="invalid-ttl",
        ),
    ],
)
@patch.object(cfn_resource_provider.ResourceProvider, "send_response")
def test_invalid_payload(_, event: RequestProperties, reason: str) -> None:
    provider = CrossAccountDNSProvider()
    response = provider.handle(event, {})
    assert response["Status"] == "FAILED"
    assert response["Reason"].startswith(reason)
