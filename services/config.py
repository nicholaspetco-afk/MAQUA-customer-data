"""Configuration for MAQUA membership service."""

APP_KEY = "5eb18c62078542728cf3c63f34906775"
APP_SECRET = "aee93787cf51f588766183987331fe6d11bfd234"
TENANT_ID = "i65qty77"
TOKEN_URL = "https://c2.yonyoucloud.com/iuap-api-auth"
GATEWAY_URL = "https://c2.yonyoucloud.com/iuap-api-gateway"

FOLLOWUP_LIST_PATH = "/yonbip/crm/followup/list"
# 使用精準編碼查詢，避免模糊匹配導致跨客戶結果
FOLLOWUP_CUSTOMER_FIELD = "customer.code"
FOLLOWUP_SEARCH_OPERATOR = "eq"
CUSTOMER_DETAIL_PATH = "/yonbip/crm/customer/getbyid"
CUSTOMER_ADDRESS_LIST_PATH = "/yonbip/digitalModel/merchant/listaddressbycodelist"
SELF_APP_TOKEN_PATH = "/open-auth/selfAppAuth/base/v1/getAccessToken"

TASK_LIST_PATH = "/yonbip/crm/task/list"
TASK_CUSTOMER_FIELD = "customer.name"
TASK_CUSTOMER_OPERATOR = "like"
MAINTENANCE_TASK_OWNER_KEYWORD = "客服003"
OPPORTUNITY_LIST_PATH = "/yonbip/crm/oppt/bill/list"
OPPORTUNITY_DETAIL_PATH = "/yonbip/crm/oppt/getbyid"
OPPORTUNITY_REPEAT_CHECK_PATH = "/yonbip/crm/bill/opptcheckrepeat"
OPPORTUNITY_CUSTOMER_FIELD = "customer.code"
OPPORTUNITY_CUSTOMER_OPERATOR = "eq"
OPPORTUNITY_DETAIL_WEB_URL_TEMPLATE = ""


DEFAULT_PAGE_SIZE = 20
DEFAULT_TASK_PAGE_SIZE = 50
