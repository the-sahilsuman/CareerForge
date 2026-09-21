import apiClient from "./client";

export async function getProjects() {
  return apiClient.get("/api/v1/projects");
}

export async function createProject(data) {
  return apiClient.post(
    "/api/v1/projects",
    data
  );
}

export async function updateProject(id, data) {
  return apiClient.patch(
    `/api/v1/projects/${id}`,
    data
  );
}

export async function deleteProject(id) {
  return apiClient.delete(
    `/api/v1/projects/${id}`
  );
}