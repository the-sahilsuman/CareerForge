import api from "./client";

export async function testBackendConnection() {
  return api.get("/health");
}