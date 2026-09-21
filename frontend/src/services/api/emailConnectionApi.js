import apiClient from "./client";

export async function getEmailConnections() {
  return apiClient.get(
    "/api/v1/email-connections"
  );
}

export async function getGoogleAuthorizationUrl() {
  return apiClient.get(
    "/api/v1/email-connections/google"
  );
}

export async function disconnectEmailConnection(
  connectionId
) {
  return apiClient.delete(
    `/api/v1/email-connections/${connectionId}`
  );
}