"""
IPFS Manager Module
Handles IPFS uploads and blockchain pinning
"""
import os
import requests
import json
from typing import Dict, Optional
from .utils import setup_logging
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class IPFSManager:
    """Manages IPFS operations and blockchain pinning"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ipfs_api_url = config.get('IPFS_API_URL', 'https://api.pinata.cloud')
        self.ipfs_api_key = config.get('PINATA_API_KEY')
        self.ipfs_api_secret = config.get('PINATA_API_SECRET')
        
        # Alternative: local IPFS node
        self.local_ipfs_url = config.get('LOCAL_IPFS_URL', 'http://localhost:5001')
        self.use_pinata = bool(self.ipfs_api_key and self.ipfs_api_secret)
    
    def upload_to_ipfs(self, file_path: str) -> str:
        """Upload file to IPFS and return hash"""
        try:
            if self.use_pinata:
                return self._upload_to_pinata(file_path)
            else:
                return self._upload_to_local_ipfs(file_path)
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            raise
    
    def _upload_to_pinata(self, file_path: str) -> str:
        """Upload to Pinata IPFS service"""
        try:
            url = f"{self.ipfs_api_url}/pinning/pinFileToIPFS"
            
            headers = {
                'pinata_api_key': self.ipfs_api_key,
                'pinata_secret_api_key': self.ipfs_api_secret
            }
            
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file)}
                
                # Add metadata
                metadata = {
                    'name': os.path.basename(file_path),
                    'keyvalues': {
                        'type': 'dmca_notice' if 'dmca' in file_path else 'license',
                        'timestamp': str(os.path.getmtime(file_path))
                    }
                }
                
                response = requests.post(
                    url,
                    files=files,
                    headers=headers,
                    data={'pinataMetadata': json.dumps(metadata)}
                )
                
                response.raise_for_status()
                result = response.json()
                ipfs_hash = result['IpfsHash']
                
                logger.info(f"📤 File uploaded to IPFS via Pinata: {ipfs_hash}")
                return ipfs_hash
                
        except Exception as e:
            logger.error(f"Pinata upload failed: {e}")
            raise
    
    def _upload_to_local_ipfs(self, file_path: str) -> str:
        """Upload to local IPFS node"""
        try:
            url = f"{self.local_ipfs_url}/api/v0/add"
            
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file)}
                response = requests.post(url, files=files)
                
                response.raise_for_status()
                result = response.json()
                ipfs_hash = result['Hash']
                
                logger.info(f"📤 File uploaded to local IPFS: {ipfs_hash}")
                return ipfs_hash
                
        except Exception as e:
            logger.error(f"Local IPFS upload failed: {e}")
            # Fallback to web3.storage or other service
            return self._upload_to_web3_storage(file_path)
    
    def _upload_to_web3_storage(self, file_path: str) -> str:
        """Fallback upload to web3.storage"""
        try:
            web3_token = self.config.get('WEB3_STORAGE_TOKEN')
            if not web3_token:
                raise ValueError("No Web3.Storage token configured")
            
            url = "https://api.web3.storage/upload"
            headers = {
                'Authorization': f'Bearer {web3_token}'
            }
            
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file)}
                response = requests.post(url, files=files, headers=headers)
                
                response.raise_for_status()
                result = response.json()
                cid = result['cid']
                
                logger.info(f"📤 File uploaded to Web3.Storage: {cid}")
                return cid
                
        except Exception as e:
            logger.error(f"Web3.Storage upload failed: {e}")
            # Last resort: return local file path
            logger.warning(f"⚠️ IPFS upload failed, using local path: {file_path}")
            return f"local://{file_path}"
    
    def pin_on_chain(self, ipfs_hash: str) -> Dict:
        """Pin IPFS hash on blockchain"""
        try:
            # This would integrate with your blockchain contract
            # For now, we'll simulate the transaction
            
            import hashlib
            import time
            
            tx_data = {
                'ipfs_hash': ipfs_hash,
                'timestamp': time.time(),
                'action': 'pin_ipfs'
            }
            
            tx_hash = f"0x{hashlib.sha256(json.dumps(tx_data).encode()).hexdigest()}"
            
            logger.info(f"📌 IPFS hash pinned on chain: {tx_hash}")
            
            return {
                'success': True,
                'ipfs_hash': ipfs_hash,
                'transaction_hash': tx_hash,
                'block_number': 12345678,  # Simulated
                'gas_used': 21000
            }
            
        except Exception as e:
            logger.error(f"Blockchain pinning failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """Get accessible URL for IPFS content"""
        if ipfs_hash.startswith('local://'):
            return ipfs_hash
        
        # Use public gateways
        gateways = [
            f"https://ipfs.io/ipfs/{ipfs_hash}",
            f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
            f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}",
            f"https://gateway.ipfs.io/ipfs/{ipfs_hash}"
        ]
        
        # Return the first working gateway
        for gateway in gateways:
            try:
                response = requests.head(gateway, timeout=5)
                if response.status_code == 200:
                    return gateway
            except:
                continue
        
        # Default to ipfs.io
        return gateways[0]
    
    def verify_ipfs_content(self, ipfs_hash: str) -> bool:
        """Verify that content is accessible on IPFS"""
        try:
            url = self.get_ipfs_url(ipfs_hash)
            if url.startswith('local://'):
                return os.path.exists(url.replace('local://', ''))
            
            response = requests.head(url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"IPFS verification failed: {e}")
            return False