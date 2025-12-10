"""
NetSuite API Connector
Handles authentication and API requests to NetSuite RESTlet endpoints
"""

import requests
import json
import hashlib
import hmac
import base64
import time
import random
import string
from urllib.parse import quote
from typing import Dict, List, Optional, Any


class NetSuiteConnector:
    """
    NetSuite RESTlet connector using OAuth 1.0 authentication
    """
    
    def __init__(self, account_id: str, consumer_key: str, consumer_secret: str, 
                 token_id: str, token_secret: str, restlet_url: Optional[str] = None):
        """
        Initialize NetSuite connector
        
        Args:
            account_id: NetSuite account ID (e.g., '1234567')
            consumer_key: OAuth consumer key from integration record
            consumer_secret: OAuth consumer secret from integration record
            token_id: Token ID from token-based authentication
            token_secret: Token secret from token-based authentication
            restlet_url: Optional custom RESTlet URL (defaults to standard URL)
        """
        self.account_id = account_id.upper().replace('_', '-')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret
        
        # Default RESTlet URL - update this with your actual deployed RESTlet URL
        self.restlet_url = restlet_url or f"https://{self.account_id.lower()}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"
        
        self.realm = account_id.upper()
    
    def _generate_nonce(self, length: int = 11) -> str:
        """Generate random nonce for OAuth"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_timestamp(self) -> str:
        """Generate current timestamp"""
        return str(int(time.time()))
    
    def _generate_signature(self, method: str, url: str, oauth_params: Dict[str, str]) -> str:
        """
        Generate OAuth 1.0 signature
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL being called
            oauth_params: OAuth parameters dictionary
            
        Returns:
            Base64-encoded signature
        """
        # Create base string
        sorted_params = sorted(oauth_params.items())
        param_string = '&'.join([f"{quote(str(k), safe='')}={quote(str(v), safe='')}" 
                                for k, v in sorted_params])
        
        base_string = '&'.join([
            method.upper(),
            quote(url, safe=''),
            quote(param_string, safe='')
        ])
        
        # Create signing key
        signing_key = f"{quote(self.consumer_secret, safe='')}&{quote(self.token_secret, safe='')}"
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _create_oauth_header(self, method: str, url: str) -> str:
        """
        Create OAuth 1.0 authorization header
        
        Args:
            method: HTTP method
            url: Request URL
            
        Returns:
            OAuth authorization header string
        """
        oauth_params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': self.token_id,
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': self._generate_timestamp(),
            'oauth_nonce': self._generate_nonce(),
            'oauth_version': '1.0'
        }
        
        # Generate signature
        oauth_params['oauth_signature'] = self._generate_signature(method, url, oauth_params)
        
        # Build header
        oauth_header = 'OAuth realm="' + self.realm + '"'
        for key, value in sorted(oauth_params.items()):
            oauth_header += f', {key}="{quote(str(value), safe="")}"'
        
        return oauth_header
    
    def make_request(self, method: str = "POST", params: Optional[Dict] = None, 
                    payload: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to NetSuite RESTlet
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            params: URL parameters
            payload: Request body data
            
        Returns:
            JSON response from NetSuite
        """
        url = self.restlet_url
        
        # Add query parameters to URL if GET request
        if method.upper() == "GET" and params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        # Create OAuth header
        auth_header = self._create_oauth_header(method.upper(), url)
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=60)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=payload, timeout=60)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=payload, timeout=60)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"NetSuite API request failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test NetSuite connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test query
            payload = {
                "action": "test_connection"
            }
            response = self.make_request(method="POST", payload=payload)
            return response.get('status') == 'success'
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
    
    def get_sales_transactions(self, start_date: str, end_date: str, 
                              filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get sales transactions from NetSuite
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            filters: Optional filters (category, vendor, etc.)
            
        Returns:
            List of transaction records
        """
        payload = {
            "action": "get_sales_transactions",
            "start_date": start_date,
            "end_date": end_date,
            "filters": filters or {}
        }
        
        response = self.make_request(method="POST", payload=payload)
        return response.get('data', [])
    
    def get_item_master(self, item_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get item master data
        
        Args:
            item_ids: Optional list of specific item IDs to retrieve
            
        Returns:
            List of item records
        """
        payload = {
            "action": "get_item_master",
            "item_ids": item_ids or []
        }
        
        response = self.make_request(method="POST", payload=payload)
        return response.get('data', [])
    
    def get_customer_master(self, customer_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get customer master data
        
        Args:
            customer_ids: Optional list of specific customer IDs to retrieve
            
        Returns:
            List of customer records
        """
        payload = {
            "action": "get_customer_master",
            "customer_ids": customer_ids or []
        }
        
        response = self.make_request(method="POST", payload=payload)
        return response.get('data', [])
    
    def execute_saved_search(self, search_id: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a NetSuite saved search
        
        Args:
            search_id: Internal ID of the saved search
            filters: Optional runtime filters
            
        Returns:
            List of search result records
        """
        payload = {
            "action": "execute_saved_search",
            "search_id": search_id,
            "filters": filters or {}
        }
        
        response = self.make_request(method="POST", payload=payload)
        return response.get('data', [])
    
    def get_cost_retail_data(self, item_ids: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Get corrected cost and retail data from merchandising
        This should pull from the cost/retail master maintained by Annie
        
        Args:
            item_ids: Optional list of item IDs
            
        Returns:
            Dictionary mapping item_id to {cost, retail} data
        """
        payload = {
            "action": "get_cost_retail_data",
            "item_ids": item_ids or []
        }
        
        response = self.make_request(method="POST", payload=payload)
        return response.get('data', {})
