from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
import base64
import os
from docusign_esign import (
    ApiClient, EnvelopesApi, EnvelopeDefinition, 
    Document, Signer, SignHere, Tabs, RecipientRouting
)

app = FastAPI(title="DocuSign Multi-Signer API")

# --- Pydantic Schemas for Input Validation ---
class SignerModel(BaseModel):
    name: str
    email: EmailStr

class DocumentSignatureRequest(BaseModel):
    document_path: str  # Path to the local PDF file to be signed
    signer_one: SignerModel
    signer_two: SignerModel


# --- Helper Function to Create the Envelope ---
def make_envelope(args: dict) -> EnvelopeDefinition:
    # 1. Read and encode the document
    with open(args["document_path"], "rb") as file:
        doc_bytes = file.read()
    doc_b64 = base64.b64encode(doc_bytes).decode("ascii")

    document = Document(
        document_base64=doc_b64,
        name="Mutual Agreement",
        file_extension="pdf",
        document_id="1"
    )

    # 2. Define Signer 1 (Receives the document first)
    signer1 = Signer(
        email=args["signer_one_email"],
        name=args["signer_one_name"],
        recipient_id="1",
        routing_order="1" # Sequential routing
    )
    
    # Place Signer 1's signature tab (Coordinates on the page)
    sign_here1 = SignHere(
        document_id="1", page_number="1", 
        x_position="100", y_position="150"
    )
    signer1.tabs = Tabs(sign_here_tabs=[sign_here1])

    # 3. Define Signer 2 (Receives the document AFTER Signer 1 signs)
    signer2 = Signer(
        email=args["signer_two_email"],
        name=args["signer_two_name"],
        recipient_id="2",
        routing_order="2" # Must be '1' if you want them to sign in parallel
    )
    
    # Place Signer 2's signature tab further down
    sign_here2 = SignHere(
        document_id="1", page_number="1", 
        x_position="100", y_position="300"
    )
    signer2.tabs = Tabs(sign_here_tabs=[sign_here2])

    # 4. Assemble the envelope definition
    envelope_definition = EnvelopeDefinition(
        email_subject="Action Required: Please sign this document",
        documents=[document],
        recipients={"signers": [signer1, signer2]},
        status="sent" # "sent" sends it immediately; "created" saves it as a draft
    )
    
    return envelope_definition


# --- The FastAPI Endpoint ---
@app.post("/api/v1/signatures/initiate", status_code=status.HTTP_201_CREATED)
async def initiate_signature(payload: DocumentSignatureRequest):
    # Ensure environment variables for DocuSign Auth are available
    # In production, look into DocuSign JWT Grant authentication
    access_token = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    account_id = os.getenv("DOCUSIGN_ACCOUNT_ID")
    base_url = os.getenv("DOCUSIGN_BASE_URL", "https://demo.docusign.net/restapi")

    if not access_token or not account_id:
        raise HTTPException(
            status_code=500, 
            detail="DocuSign authentication environment variables are missing."
        )

    if not os.path.exists(payload.document_path):
        raise HTTPException(status_code=400, detail="Target document file not found.")

    try:
        # Initialize DocuSign API Client
        api_client = ApiClient()
        api_client.host = base_url
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        
        envelopes_api = EnvelopesApi(api_client)

        # Construct the payload mapping
        envelope_args = {
            "document_path": payload.document_path,
            "signer_one_email": payload.signer_one.email,
            "signer_one_name": payload.signer_one.name,
            "signer_two_email": payload.signer_two.email,
            "signer_two_name": payload.signer_two.name,
        }

        envelope_def = make_envelope(envelope_args)

        # Call DocuSign API to create and send the envelope
        results = envelopes_api.create_envelope(
            account_id=account_id, 
            envelope_definition=envelope_def
        )

        return {
            "status": "success",
            "envelope_id": results.envelope_id,
            "message": "Envelope successfully created and sent to recipients."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DocuSign Error: {str(e)}")