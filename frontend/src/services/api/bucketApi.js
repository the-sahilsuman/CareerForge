import apiClient from "./client";


export async function getBuckets() {
  return apiClient.get(
    "/api/v1/buckets"
  );
}


export async function createBucket(data) {
  return apiClient.post(
    "/api/v1/buckets",
    data
  );
}


export async function updateBucket(
  bucketId,
  data
) {
  return apiClient.patch(
    `/api/v1/buckets/${bucketId}`,
    data
  );
}


export async function deleteBucket(
  bucketId
) {
  return apiClient.delete(
    `/api/v1/buckets/${bucketId}`
  );
}