import apiClient from "./client";


export async function provisionUser(username) {
    return apiClient.post(
        "/api/v1/users/provision",
        {
            username: username.trim(),
        },
        {
            authenticated: false,
        }
    );
}


export async function bootstrapCurrentUser() {
    return apiClient.post(
        "/api/v1/users/me"
    );
}