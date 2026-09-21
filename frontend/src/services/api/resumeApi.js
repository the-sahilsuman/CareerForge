import apiClient from "./client";

/*
|--------------------------------------------------------------------------
| Get all resumes for current user
|--------------------------------------------------------------------------
*/
export async function getResumes() {
  const response = await apiClient.get(
    "/api/v1/resumes"
  );
//   console.log("========== GET /resumes ==========");
//   console.log("apiClient returned:", response);
//   console.log("isArray:", Array.isArray(response));
//   console.log("length:", Array.isArray(response) ? response.length : "N/A");
//   console.log("==================================");


//   return Array.isArray(response)
//     ? response
//     : response?.data ?? [];
     return response   
}

/*
|--------------------------------------------------------------------------
| Upload resume
|--------------------------------------------------------------------------
|
| IMPORTANT:
| Do NOT set Content-Type manually.
| The browser adds:
|
| multipart/form-data; boundary=----...
|
|--------------------------------------------------------------------------
*/
export async function uploadResume(file) {
  if (!file) {
    throw new Error("Please select a resume file.");
  }

  const formData = new FormData();

  formData.append("file", file);

  return apiClient.post(
    "/api/v1/resumes/upload",
    formData
  );
}

/*
|--------------------------------------------------------------------------
| Delete resume
|--------------------------------------------------------------------------
*/
export async function deleteResume(resumeId) {
  return apiClient.delete(
    `/api/v1/resumes/${resumeId}`
  );
}

/*
|--------------------------------------------------------------------------
| Get one resume
|--------------------------------------------------------------------------
*/
export async function getResume(resumeId) {
  return apiClient.get(
    `/api/v1/resumes/${resumeId}`
  );
}