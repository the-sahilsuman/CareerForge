import apiClient from "./client";


export async function getEmailRecords() {
  return apiClient.get(
    "/api/v1/emails"
  );
}