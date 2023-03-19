from cfn_cross_account_dns_provider import cross_account_dns


def handler(request, context):
    return cross_account_dns.handler(request, context)
