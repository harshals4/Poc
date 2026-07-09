from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import docusign_esign as docusign
import os
import json
import base64


router = APIRouter(prefix="/docsign", tags=["documentsign"])


DOCUSIGN_AUTH_SERVER = "account-d.docusign.com" # 'account-d' is for the demo/dev environment


DOCUSIGN_CLIENT_ID = os.getenv("DOCUSIGN_CLIENT_ID")
DOCUSIGN_USER_ID = os.getenv("DOCUSIGN_USER_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
BASE_PATH = os.getenv("BASE_PATH")


json_data = {"name": "Ahmedabad", "type": "City"}

# Convert JSON to string and then encode to Base64
json_string = json.dumps(json_data)
base64_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

# --- Models ---
class SignerRequest(BaseModel):
    signer_email: str
    signer_name: str
    # document_base64: str # A simple base64 encoded PDF or TXT file

# --- Helper Functions ---
# def get_docusign_client():
#     """Authenticates using JWT and returns the API client."""
#     api_client = docusign.ApiClient()
#     api_client.set_base_path(DOCUSIGN_AUTH_SERVER)
    
#     try:
#         with open(PRIVATE_KEY_PATH, "rb") as key_file:
#             private_key = key_file.read()
#         # Get the OAuth token
#         token_response = api_client.request_jwt_user_token(
#             client_id=DOCUSIGN_CLIENT_ID,
#             user_id=DOCUSIGN_USER_ID,
#             oauth_host_name=DOCUSIGN_AUTH_SERVER,
#             private_key_bytes=private_key,
#             expires_in=3600,
#             scopes=["signature", "impersonation"]
#         )
#         print("this line works")
#         # Configure the client with the token and proper base path
#         api_client.set_default_header("Authorization", f"Bearer {token_response.access_token}")
#         print("this line works")
#         api_client.set_base_path(BASE_PATH)
#         print("this line works")
#         return api_client
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


def get_docusign_client():
    """Gets the token, then returns a FRESH client specifically for API calls."""
    # --- 1. THE AUTHENTICATION CLIENT ---
    auth_client = docusign.ApiClient()
    auth_client.set_oauth_host_name(DOCUSIGN_AUTH_SERVER)
    
    try:
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = key_file.read()
            
        token_response = auth_client.request_jwt_user_token(
            client_id=DOCUSIGN_CLIENT_ID,
            user_id=DOCUSIGN_USER_ID,
            oauth_host_name=DOCUSIGN_AUTH_SERVER,
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=["signature", "impersonation"]
        )
        access_token = token_response.access_token
        
        # --- 2. THE API CLIENT (BRAND NEW) ---
        # We destroy the auth client and make a fresh one so the URLs don't cross streams
        api_client = docusign.ApiClient()
        
        # Explicitly set the host property (this is much safer than set_base_path)
        api_client.host = "https://demo.docusign.net/restapi"
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        
        # For now, hardcode your true Account ID here (the GUID you verified in the test script)
        true_account_id = ACCOUNT_ID
        
        return api_client, true_account_id
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


# def create_envelope(request: SignerRequest) -> docusign.EnvelopeDefinition:
#     """Builds the envelope payload with the document and signer details."""
#     # 1. Create the document model
#     document = docusign.Document(
#         document_base64=base64_data,
#         name="Marketplace Agreement",
#         file_extension="txt",
#         document_id="1"
#     )

#     # 2. Create the signer model
#     signer = docusign.Signer(
#         email=request.signer_email,
#         name=request.signer_name,
#         recipient_id="1",
#         routing_order="1"
#     )

#     # 3. Add a sign here tab (where the user actually signs)
#     sign_here = docusign.SignHere(
#         anchor_string="**signature_1**", # Places signature wherever this text appears in the doc
#         anchor_units="pixels",
#         anchor_y_offset="10",
#         anchor_x_offset="20"
#     )
    
#     # Add the tabs to the signer
#     signer.tabs = docusign.Tabs(sign_here_tabs=[sign_here])

#     # 4. Construct the final envelope
#     envelope_definition = docusign.EnvelopeDefinition(
#         email_subject="Please sign your Marketplace Agreement",
#         documents=[document],
#         recipients=docusign.Recipients(signers=[signer]),
#         status="sent" # "sent" sends it immediately, "created" saves as draft
#     )
    

def create_envelope(request: SignerRequest) -> docusign.EnvelopeDefinition:
    document = docusign.Document(
        document_base64=base64_data,
        name="Marketplace Agreement",
        file_extension="txt", 
        document_id="1"
    )

    signer = docusign.Signer(
        email=request.signer_email,
        name=request.signer_name,
        recipient_id="1",
        routing_order="1",
        client_user_id="1000" # <--- NEW: This triggers Embedded Signing
    )

    sign_here = docusign.SignHere(
        anchor_string="**signature_1**",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )
    
    signer.tabs = docusign.Tabs(sign_here_tabs=[sign_here])

    return docusign.EnvelopeDefinition(
        email_subject="Please sign your Marketplace Agreement",
        documents=[document],
        recipients=docusign.Recipients(signers=[signer]),
        status="sent"
    )  
    return envelope_definition

# --- Endpoints ---
# @router.post("/send-document")
# async def send_document_for_signature(request: SignerRequest):
#     """Endpoint to trigger the DocuSign workflow."""
#     api_client = get_docusign_client()
#     envelope_api = docusign.EnvelopesApi(api_client)
    
#     envelope_definition = create_envelope(request)
#     try:
#         results = envelope_api.create_envelope(
#             account_id=ACCOUNT_ID, 
#             envelope_definition=envelope_definition
#         )
#         return {"status": "success", "envelope_id": results.envelope_id}
#     except docusign.ApiException as e:
#         raise HTTPException(status_code=400, detail=f"DocuSign API Error: {e.body}")


# @router.post("/send-document")
# async def send_document_for_signature(request: SignerRequest):
    
#     # 1. UNPACK THE TUPLE HERE
#     api_client, true_account_id = get_docusign_client() 
    
#     # 2. Pass the clean api_client object
#     envelope_api = docusign.EnvelopesApi(api_client)
    
#     envelope_definition = create_envelope(request)
    
#     try:
#         results = envelope_api.create_envelope(
#             # 3. Use the dynamic true_account_id here!
#             account_id=true_account_id, 
#             envelope_definition=envelope_definition
#         )
#         return {"status": "success", "envelope_id": results.envelope_id}
#     except docusign.ApiException as e:
#         raise HTTPException(status_code=400, detail=f"DocuSign API Error: {e.body}")
    


from fastapi.responses import FileResponse
import tempfile

@router.get("/download-document/{envelope_id}")
async def download_signed_document(envelope_id: str):
    # 1. Get a fresh API client
    api_client, true_account_id = get_docusign_client()
    envelope_api = docusign.EnvelopesApi(api_client)
    
    try:
        # 2. Check the status of the envelope first
        envelope = envelope_api.get_envelope(true_account_id, envelope_id)
        
        if envelope.status != "completed":
            return {"message": f"Document is not fully signed yet. Current status: {envelope.status}"}
            
        # 3. If completed, download Document ID "1" (the one we created)
        # The SDK returns the file path where it temporarily saved the PDF
        temp_file_path = envelope_api.get_document(
            account_id=true_account_id,
            envelope_id=envelope_id,
            document_id="1" 
        )
        
        # 4. Return the PDF to the user/frontend
        return FileResponse(
            path=temp_file_path, 
            media_type="application/pdf", 
            filename=f"signed_agreement_{envelope_id}.pdf"
        )
        
    except docusign.ApiException as e:
        raise HTTPException(status_code=400, detail=f"DocuSign API Error: {e.body}")
    


@router.post("/send-document")
async def send_document_for_signature(request: SignerRequest):
    api_client, true_account_id = get_docusign_client() 
    envelope_api = docusign.EnvelopesApi(api_client)
    
    envelope_definition = create_envelope(request)
    
    try:
        # 1. Create the envelope
        results = envelope_api.create_envelope(
            account_id=true_account_id, 
            envelope_definition=envelope_definition
        )
        
        # 2. Request the Embedded Signing URL
        recipient_view_request = docusign.RecipientViewRequest(
            authentication_method="none",
            client_user_id="1000", # MUST match what you put in create_envelope
            recipient_id="1",
            return_url="http://localhost:8080/api/v1/success", # Where DocuSign sends them after signing
            user_name=request.signer_name,
            email=request.signer_email
        )
        
        # 3. Generate the URL
        view_url = envelope_api.create_recipient_view(
            account_id=true_account_id,
            envelope_id=results.envelope_id,
            recipient_view_request=recipient_view_request
        )
        
        # Return the URL to your frontend
        return {
            "status": "success", 
            "envelope_id": results.envelope_id,
            "signing_url": view_url.url
        }
        
    except docusign.ApiException as e:
        raise HTTPException(status_code=400, detail=f"DocuSign API Error: {e.body}")