from unittest.mock import patch
import cfn_cross_account_dns_provider
from cfn_cross_account_dns_provider import handler
from .shared_resources import Request, SnsWrapper


@patch.object(cfn_cross_account_dns_provider.cross_account_dns.CrossAccountDNSProvider, "handle", return_value={"Foo": "Bar"})
def test_handler(mock_handle) -> None:
    request = Request(
        "Create",
        name="www.example.com",
        type="CNAME",
        value="cname.example.com",
        ttl=300,
    )
    assert [{'Foo': 'Bar'}] == handler(SnsWrapper([request]), {})


@patch.object(cfn_cross_account_dns_provider.cross_account_dns.CrossAccountDNSProvider, "handle", return_value={"Foo": "Bar"})
def test_handler_multiple(mock_handle) -> None:
    request1 = Request(
        "Create",
        name="www.example1.com",
        type="CNAME",
        value="cname.example.com",
        ttl=300,
    )
    request2 = Request(
        "Create",
        name="www.example2.com",
        type="CNAME",
        value="cname.example.com",
        ttl=300,
    )
    assert [{'Foo': 'Bar'}, {'Foo': 'Bar'}] == handler(SnsWrapper([request1, request2]), {})
