import cfn_resource_provider
from unittest.mock import patch
from botocore.stub import Stubber
from cfn_cross_account_dns_provider.cross_account_dns import CrossAccountDNSProvider, client

from .shared_resources import Request, Route53Request, Route53Response


@patch.object(cfn_resource_provider.ResourceProvider, "send_response")
def test_a_record(_) -> None:
    provider = CrossAccountDNSProvider()
    request = Request("Create", name="www.example.com", type="A", value="127.0.0.1")

    with Stubber(client) as stubber:
        stubber.add_response(
            "change_resource_record_sets",
            service_response=Route53Response(),
            expected_params=Route53Request(
                action="CREATE",
                name="www.example.com",
                type="A",
                value="127.0.0.1",
                ttl=900,
            ),
        )
        response = provider.handle(request, {})
        stubber.assert_no_pending_responses()
        assert response["Status"] == "SUCCESS", response["Reason"]
        physical_resource_id = response["PhysicalResourceId"]

    # Update A record, without changes
    request["RequestType"] = "Update"
    request["PhysicalResourceId"] = physical_resource_id
    response = provider.handle(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert response["Reason"] == "nothing to change"
    assert physical_resource_id == response["PhysicalResourceId"]

    # Update A record, without replacement
    request["OldResourceProperties"] = request["ResourceProperties"].copy()
    request["ResourceProperties"]["Value"] = "127.0.0.2"

    with Stubber(client) as stubber:
        stubber.add_response(
            "change_resource_record_sets",
            service_response=Route53Response(),
            expected_params=Route53Request(
                action="UPSERT",
                name="www.example.com",
                type="A",
                value="127.0.0.2",
                ttl=900,
            ),
        )
        response = provider.handle(request, {})
        stubber.assert_no_pending_responses()
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id == response["PhysicalResourceId"]

    # Update A record, with replacement
    request["OldResourceProperties"] = request["ResourceProperties"].copy()
    request["ResourceProperties"]["Name"] = "www.other-example.com"
    with Stubber(client) as stubber:
        stubber.add_response(
            "change_resource_record_sets",
            service_response=Route53Response(),
            expected_params=Route53Request(
                action="UPSERT",
                name="www.other-example.com",
                type="A",
                value="127.0.0.2",
                ttl=900,
            ),
        )
        response = provider.handle(request, {})
        stubber.assert_no_pending_responses()
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id != response["PhysicalResourceId"]
        physical_resource_id = response["PhysicalResourceId"]

    # Delete A record, with replacement
    del request["OldResourceProperties"]
    request["PhysicalResourceId"] = physical_resource_id
    request["RequestType"] = "Delete"
    with Stubber(client) as stubber:
        stubber.add_response(
            "change_resource_record_sets",
            service_response=Route53Response(),
            expected_params=Route53Request(
                action="DELETE",
                name="www.other-example.com",
                type="A",
                value="127.0.0.2",
                ttl=900,
            ),
        )
        response = provider.handle(request, {})
        stubber.assert_no_pending_responses()
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id == response["PhysicalResourceId"]
