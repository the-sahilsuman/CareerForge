import apiClient from "./client";

export async function getCertifications() {
  return apiClient.get(
    "/api/v1/certifications"
  );
}

export async function createCertification(data) {
  return apiClient.post(
    "/api/v1/certifications",
    data
  );
}

export async function updateCertification(
  id,
  data
) {
  return apiClient.patch(
    `/api/v1/certifications/${id}`,
    data
  );
}

export async function deleteCertification(id) {
  return apiClient.delete(
    `/api/v1/certifications/${id}`
  );
}