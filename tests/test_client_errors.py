import cfn_resource_provider
from unittest.mock import patch
from botocore.stub import Stubber
from cfn_cross_account_dns_provider.cross_account_dns import CrossAccountDNSProvider, client
from tests.shared_resources import Request


@patch.object(cfn_resource_provider.ResourceProvider, "send_response")
def test_delete_non_existing_record(_) -> None:
    # Delete A record for CloudFront
    provider = CrossAccountDNSProvider()
    request = Request("Delete", name="www.example.com", type="A", value="127.0.0.1")

    with Stubber(client) as stubber:
        stubber.add_client_error(
            "change_resource_record_sets",
            "InvalidChangeBatch",
            "CustomMessage",
        )
        response = provider.handle(request, {})
        stubber.assert_no_pending_responses()
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert response["Reason"].startswith(
            "Ignore failure to delete record: An error occurred (InvalidChangeBatch) when calling the ChangeResourceRecordSets operation: CustomMessage"
        )
