import apiClient from "./client";

export async function getSkills() {
  return apiClient.get("/api/v1/skills");
}

export async function createSkill(data) {
  return apiClient.post(
    "/api/v1/skills",
    data
  );
}

export async function updateSkill(id, data) {
  return apiClient.patch(
    `/api/v1/skills/${id}`,
    data
  );
}

export async function deleteSkill(id) {
  return apiClient.delete(
    `/api/v1/skills/${id}`
  );
}