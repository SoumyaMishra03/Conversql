// src/utils/secureFetch.ts

import { generateSymmetricKey, wrapSymmetricKey, encryptPayload, decryptPayload } from "./encryption";
import { API_BASE_URL } from "@/config/api";

// This will cache the public key after the first fetch.
let serverPublicKey: string | null = null;

const getPublicKey = async (): Promise<string> => {
  if (serverPublicKey) {
    return serverPublicKey;
  }
  const response = await fetch(`${API_BASE_URL}/public-key`);
  if (!response.ok) throw new Error("Could not fetch server public key.");
  const data = await response.json();
  serverPublicKey = data.public_key;
  return serverPublicKey as string;
};

/**
 * Performs an end-to-end encrypted fetch request.
 * Encrypts the request and decrypts the response.
 */
export const secureFetch = async (endpoint: string, payload: object): Promise<any> => {
  const publicKeyPem = await getPublicKey();
  
  // 1. Generate a temporary symmetric key for this request
  const symmetricKey = await generateSymmetricKey();

  // 2. Encrypt the request payload
  const { ciphertext, nonce } = await encryptPayload(payload, symmetricKey);
  const wrappedKey = await wrapSymmetricKey(symmetricKey, publicKeyPem);

  // 3. Create the encrypted envelope for the server
  const requestBody = {
    encrypted_key: btoa(String.fromCharCode(...new Uint8Array(wrappedKey))),
    nonce: btoa(String.fromCharCode(...new Uint8Array(nonce))),
    ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
  };

  // 4. Send the request
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });

  const responseData = await response.json();

  if (!response.ok) {
    // If the server returned an error (e.g., 401, 403), it's sent in plaintext.
    return responseData;
  }

  // 5. If the response contains ciphertext, decrypt it.
  // The server uses the same symmetric key to encrypt the response.
  if (responseData.ciphertext && responseData.nonce) {
    return await decryptPayload(responseData, symmetricKey);
  }

  // Otherwise, return the plaintext JSON response (e.g., for /login)
  return responseData;
};