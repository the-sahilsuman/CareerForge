import apiClient from "./client";

export async function getExperience() {
  return apiClient.get(
    "/api/v1/experience"
  );
}

export async function createExperience(data) {
  return apiClient.post(
    "/api/v1/experience",
    data
  );
}

export async function updateExperience(
  id,
  data
) {
  return apiClient.patch(
    `/api/v1/experience/${id}`,
    data
  );
}

export async function deleteExperience(id) {
  return apiClient.delete(
    `/api/v1/experience/${id}`
  );
}