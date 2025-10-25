"""Minimal CRM client used by the membership service."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Sequence

import requests

from . import config
from .token_service import TOKEN_SERVICE


class CRMClient:
    def __init__(self) -> None:
        self.gateway_url = config.GATEWAY_URL.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self.gateway_url + path
        token = TOKEN_SERVICE.get_token()
        req_params = {"access_token": token}
        if params:
            req_params.update(params)

        resp = requests.request(method, url, params=req_params, json=json_body, timeout=15)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            details: Any
            try:
                details = resp.json()
            except ValueError:
                details = resp.text
            raise RuntimeError(
                f"HTTP {resp.status_code} calling {path}: {json.dumps(details, ensure_ascii=False)}"
            ) from exc

        data = resp.json()
        if data.get("code") not in {"00000", "200", 200, "200000"}:
            raise RuntimeError(f"CRM API error: {json.dumps(data, ensure_ascii=False)}")
        return data

    def get_followups(
        self,
        keyword: str,
        *,
        page: int = 1,
        page_size: int = 10,
        search_field: Optional[str] = None,
        search_operator: Optional[str] = None,
        value_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "pageIndex": page,
            "pageSize": page_size,
        }
        if keyword or value_override is not None:
            field = search_field or getattr(config, "FOLLOWUP_CUSTOMER_FIELD", "customer.name")
            operator_raw = search_operator or getattr(config, "FOLLOWUP_SEARCH_OPERATOR", "like")
            operator = str(operator_raw).strip()
            op_lower = operator.lower()
            op_payload = operator
            value = keyword
            try:
                has_wildcard = "%" in value or "_" in value
            except TypeError:
                has_wildcard = False
            trimmed = value.strip() if isinstance(value, str) else value
            if isinstance(trimmed, str):
                if op_lower == "like" and not has_wildcard:
                    value = f"%{trimmed}%"
                elif op_lower == "likeleft" and not trimmed.endswith("%"):
                    value = f"%{trimmed}"
                elif op_lower == "likeright" and not trimmed.startswith("%"):
                    value = f"{trimmed}%"
                else:
                    value = trimmed
            if value_override is not None:
                value = value_override
            payload["simpleVOs"] = [
                {
                    "field": field,
                    "op": op_payload,
                    "value1": value,
                }
            ]
        return self._request("POST", config.FOLLOWUP_LIST_PATH, json_body=payload)

    def get_tasks(
        self,
        customer_code: str = "",
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        task_path = getattr(config, "TASK_LIST_PATH", "").strip()
        if not task_path:
            raise RuntimeError("TASK_LIST_PATH is not configured")

        payload: Dict[str, Any] = {
            "pageIndex": page,
            "pageSize": page_size,
        }

        if customer_code:
            field = getattr(config, "TASK_CUSTOMER_FIELD", "customer.name")
            operator = getattr(config, "TASK_CUSTOMER_OPERATOR", "like")
            filter_payload: Dict[str, Any] = {
                "field": field,
                "op": operator,
                "value1": customer_code,
            }
            if operator == "between":
                filter_payload.setdefault("value2", customer_code)
            payload["simpleVOs"] = [filter_payload]

        return self._request("POST", task_path, json_body=payload)


    def get_opportunities(
        self,
        customer_code: str = "",
        *,
        page: int = 1,
        page_size: int = 20,
        field: Optional[str] = None,
        operator: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = getattr(config, "OPPORTUNITY_LIST_PATH", "").strip()
        if not path:
            return {"data": {"recordList": []}}
        payload: Dict[str, Any] = {"pageIndex": page, "pageSize": page_size}
        if customer_code:
            use_field = field or getattr(config, "OPPORTUNITY_CUSTOMER_FIELD", "customer.code")
            use_operator = operator or getattr(config, "OPPORTUNITY_CUSTOMER_OPERATOR", "eq")
            payload["simpleVOs"] = [
                {
                    "field": use_field,
                    "op": use_operator,
                    "value1": customer_code,
                }
            ]
        return self._request("POST", path, json_body=payload)

    def get_opportunity_detail(self, opportunity_id: str) -> Dict[str, Any]:
        path = getattr(config, "OPPORTUNITY_DETAIL_PATH", "").strip()
        if not path:
            return {"data": {}}
        if not opportunity_id:
            return {"data": {}}
        try:
            return self._request("GET", path, params={"id": opportunity_id})
        except RuntimeError:
            payload = {"id": opportunity_id}
            return self._request("POST", path, params={"id": opportunity_id}, json_body=payload)

    def check_opportunity_repeat(
        self,
        *,
        data: Optional[Dict[str, Any]] = None,
        system_source: str = "mt",
        action: str = "browse",
        main_bill_num: str = "sfa_opptcard",
        bill_num: Optional[str] = None,
        tab_info: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        path = getattr(config, "OPPORTUNITY_REPEAT_CHECK_PATH", "").strip()
        if not path:
            raise RuntimeError("OPPORTUNITY_REPEAT_CHECK_PATH is not configured")

        billnum_value = bill_num or main_bill_num
        payload: Dict[str, Any] = {
            "systemSource": system_source,
            "action": action,
            "mainBillNum": main_bill_num,
            "data": data or {},
            "billnum": billnum_value,
            "tabInfo": list(tab_info or [{"billNum": billnum_value, "mappingType": "0"}]),
        }
        return self._request("POST", path, json_body=payload)

    def get_customer_detail(self, customer_id: str, org_id: str) -> Dict[str, Any]:
        params = {"id": customer_id, "orgId": org_id}
        return self._request("GET", config.CUSTOMER_DETAIL_PATH, params=params)

    def get_addresses_by_codes(self, codes: Iterable[str]) -> Dict[str, Any]:
        codes_list = list(codes)
        payload = {
            "codeList": codes_list,
            "pageIndex": 1,
            "pageSize": max(len(codes_list), 1),
        }
        return self._request("POST", config.CUSTOMER_ADDRESS_LIST_PATH, json_body=payload)


CRM_CLIENT = CRMClient()
