# DocuSign Embedded Signing PoC (FastAPI)

A Proof of Concept (PoC) demonstrating how to integrate DocuSign's eSignature API into a Python/FastAPI backend. This project utilizes **JWT (JSON Web Token) Grant Authentication** to seamlessly generate envelopes and provides **Embedded Signing**, allowing users to sign documents directly within a custom application flow without waiting for emails.

## 🚀 Features

* **Server-to-Server Authentication:** Uses RSA Private Keys and JWT so the server acts autonomously without manual admin login.
* **Dynamic Routing:** Automatically queries DocuSign for the correct Account ID and Base URI to prevent environment mismatches.
* **Embedded Signing:** Generates a secure, temporary URL so users can sign the document immediately in the browser.
* **Document Retrieval:** Downloads the fully executed document as a PDF once signing is complete.

---

## 📋 Prerequisites

Before running this project, you must have a [DocuSign Developer Account](https://developers.docusign.com/). From your admin dashboard, gather the following credentials:

1. **Integration Key (Client ID)**
2. **API Username (User ID)** *(Note: This is a GUID, not your email address)*
3. **API Account ID** *(Note: This is a GUID, not the short integer Account ID)*
4. **RSA Private Key** *(Generate this in the dashboard and save the `.pem` file)*

> **⚠️ Important One-Time Admin Consent:** > Before the JWT token will work, the admin must grant the application permission to impersonate them. Construct this URL with your Integration Key, ensure `http://localhost:8080/` is added to your App's Redirect URIs, and visit it in your browser to click "Accept":
> `https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature%20impersonation&client_id=YOUR_INTEGRATION_KEY&redirect_uri=http://localhost:8080/`

---

## 🛠️ Setup & Installation

**1. Clone the repository and navigate to the project directory.**

**2. Install the required dependencies:**
```bash
pip install fastapi uvicorn docusign-esign pydantic
```



## some working expamples

# request body: 
> <img width="1462" height="682" alt="image" src="https://github.com/user-attachments/assets/1faa4605-1bf2-4813-b469-49ae037ba165" />

# response structure:
> <img width="1410" height="497" alt="image" src="https://github.com/user-attachments/assets/5c781f3c-a4df-4a5e-a8dd-d9b15592a571" />

# email notification:
> <img width="1393" height="782" alt="image" src="https://github.com/user-attachments/assets/988ca032-8533-4c87-b3ab-2bffcd515638" />

