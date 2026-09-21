import apiClient from "./client";

export async function getProfile() {
  return apiClient.get(
    "/api/v1/profile"
  );
}

export async function createProfile(data) {
  return apiClient.post(
    "/api/v1/profile",
    data
  );
}

export async function updateProfile(data) {
  return apiClient.patch(
    "/api/v1/profile",
    data
  );
}

export async function deleteProfile() {
  return apiClient.delete(
    "/api/v1/profile"
  );
}