import apiClient from "./client";


export async function sendChatMessage({
  message,
  jdId = null,
}) {
  return apiClient.post(
    "/api/v1/agentic/chat",
    {
      message,
      jd_id: jdId,
    },
    {
      timeout: 240000,
    }
  );
}


export async function getChatHistory() {
  return apiClient.get(
    "/api/v1/agentic/chat/history"
  );
}


export async function getEmailRecords() {
  return apiClient.get(
    "/api/v1/agentic/emails"
  );
}