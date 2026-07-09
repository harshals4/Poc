import docusign_esign as docusign

# --- HARDCODE YOUR EXACT VALUES HERE ---
CLIENT_ID = "44eb32dc-83cf-45b0-8d76-64006f2be2e7"
USER_ID = "261c4a8d-5d17-4baa-9801-017215b1bea6"
PRIVATE_KEY_PATH = "private.key"
# ---------------------------------------

def test_docusign_auth():
    print("1. Starting authentication test...")
    api_client = docusign.ApiClient()
    api_client.set_oauth_host_name("account-d.docusign.com")
    
    try:
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = key_file.read()
            
        print("2. Requesting JWT Token...")
        token_response = api_client.request_jwt_user_token(
            client_id=CLIENT_ID,
            user_id=USER_ID,
            oauth_host_name="account-d.docusign.com",
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=["signature", "impersonation"]
        )
        
        access_token = token_response.access_token
        print("   -> Token generated successfully!")
        
        print("3. Validating token against DocuSign servers...")
        # This is the moment of truth. If the token is invalid, it fails here.
        user_info = api_client.get_user_info(access_token)
        account = user_info.accounts[0]
        
        print("\n=== SUCCESS! YOUR KEYS ARE 100% CORRECT ===")
        print(f"True Account ID: {account.account_id}")
        print(f"True Base URI:   {account.base_uri}/restapi")
        print("===========================================\n")
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}\n")

if __name__ == "__main__":
    test_docusign_auth()