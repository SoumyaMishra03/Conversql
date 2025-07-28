// src/utils/encryption.ts

import { API_BASE_URL } from "@/config/api";

// Helper function to convert a binary string (from atob) to an ArrayBuffer.
const str2ab = (str: string): ArrayBuffer => {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
};

/**
 * [UPDATED] More robustly cleans and imports a PEM-formatted RSA public key.
 */
async function importRsaPublicKey(pem: string): Promise<CryptoKey> {
  const pemHeader = "-----BEGIN PUBLIC KEY-----";
  const pemFooter = "-----END PUBLIC KEY-----";
  
  // A more robust way to extract the key content
  const pemContents = pem
    .replace(pemHeader, "")
    .replace(pemFooter, "")
    .replace(/\s/g, ""); // Remove all whitespace characters (newlines, etc.)

  try {
    const binaryDer = window.atob(pemContents);
    const arrayBuffer = str2ab(binaryDer);

    return await crypto.subtle.importKey(
      "spki",
      arrayBuffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["wrapKey"]
    );
  } catch (error) {
    console.error("DECODING FAILED: The Base64 string is invalid.", { pemContents, error });
    throw new Error("Failed to decode the server's public key.");
  }
}

// Global cache for the server's public key
let serverPublicKey: CryptoKey | null = null;

/**
 * Fetches the server's public key from the /public-key endpoint and caches it.
 */
async function getPublicKey(): Promise<CryptoKey> {
  if (serverPublicKey) {
    return serverPublicKey;
  }
  
  const response = await fetch(`${API_BASE_URL}/public-key`);

  if (!response.ok) {
    throw new Error("Could not fetch server public key.");
  }

  const data = await response.json();
  const publicKeyContent = data.public_key;

  if (!publicKeyContent || typeof publicKeyContent !== 'string') {
      throw new Error("Received invalid public key from server.");
  }

  serverPublicKey = await importRsaPublicKey(publicKeyContent);
  return serverPublicKey;
}

/**
 * Decrypts an incoming payload from the server using the original AES-GCM key.
 */
async function decryptPayload(
  encryptedData: { nonce: string; ciphertext: string },
  symmetricKey: CryptoKey
): Promise<any> {
  const nonce = str2ab(atob(encryptedData.nonce));
  const ciphertext = str2ab(atob(encryptedData.ciphertext));

  const decryptedBuffer = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: new Uint8Array(nonce) },
    symmetricKey,
    new Uint8Array(ciphertext)
  );

  const decryptedText = new TextDecoder().decode(decryptedBuffer);
  return JSON.parse(decryptedText);
};

/**
 * Performs a full end-to-end encrypted fetch request.
 */
export const secureFetch = async (endpoint: string, payload: object): Promise<any> => {
  const publicKey = await getPublicKey();
  
  const symmetricKey = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );

  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encodedPayload = new TextEncoder().encode(JSON.stringify(payload));
  const ciphertextBuffer = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, symmetricKey, encodedPayload);

  const wrappedKeyBuffer = await crypto.subtle.wrapKey("raw", symmetricKey, publicKey, "RSA-OAEP");

  const requestBody = {
    encrypted_key: btoa(String.fromCharCode(...new Uint8Array(wrappedKeyBuffer))),
    nonce: btoa(String.fromCharCode(...new Uint8Array(iv))),
    ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertextBuffer))),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });

  const responseData = await response.json();

  if (!response.ok) {
    return responseData;
  }

  if (responseData.ciphertext && responseData.nonce) {
    return await decryptPayload(responseData, symmetricKey);
  }

  return responseData;
};