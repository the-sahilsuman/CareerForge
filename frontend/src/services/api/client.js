import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

/*
|--------------------------------------------------------------------------
| Axios instance
|--------------------------------------------------------------------------
|
| The frontend communicates only with Core Backend.
|
| Core Backend is responsible for communicating with Agentic Service.
|
| Chat requests can take longer because Core Backend waits for:
|
| Frontend
|   -> Core Backend
|   -> Agentic Service
|   -> LangGraph
|   -> Retrieval
|   -> LLM
|   -> Core Backend
|   -> Frontend
|
| Therefore the default timeout must not be too aggressive.
|--------------------------------------------------------------------------
*/

const api = axios.create({
  baseURL: API_BASE_URL,

  /*
   * Increased from 30 seconds.
   *
   * This is especially important for AI/chat requests where the
   * backend may wait for retrieval + LLM generation.
   */
  timeout: 120000,

  headers: {
    Accept: "application/json",
  },
});

/*
|--------------------------------------------------------------------------
| Request interceptor
|--------------------------------------------------------------------------
|
| Get the current Cognito session before every request.
|--------------------------------------------------------------------------
*/

api.interceptors.request.use(
  async (config) => {
    try {
      /*
       * Dynamically import authService so client.js does not
       * create an unnecessary circular dependency during startup.
       */
      const { getSession } = await import(
        "../../auth/authService"
      );

      const session = await getSession();

      let token = null;

      /*
       * Support the common Cognito session shapes.
       */

      if (session?.accessToken?.jwtToken) {
        token = session.accessToken.jwtToken;
      } else if (session?.idToken?.jwtToken) {
        token = session.idToken.jwtToken;
      } else if (
        session?.tokens?.accessToken?.toString
      ) {
        token =
          session.tokens.accessToken.toString();
      } else if (
        session?.tokens?.idToken?.toString
      ) {
        token =
          session.tokens.idToken.toString();
      } else if (session?.accessToken) {
        token =
          typeof session.accessToken === "string"
            ? session.accessToken
            : session.accessToken.toString?.();
      }

      if (token) {
        config.headers.Authorization =
          `Bearer ${token}`;
      }
    } catch (error) {
      /*
       * Do not break public requests if a session
       * cannot be restored.
       */
      console.warn(
        "Unable to attach authentication token:",
        error
      );
    }

    /*
    |--------------------------------------------------------------------------
    | IMPORTANT: Multipart/FormData
    |--------------------------------------------------------------------------
    |
    | NEVER manually set:
    |
    | Content-Type: multipart/form-data
    |
    | The browser must generate:
    |
    | multipart/form-data; boundary=----...
    |--------------------------------------------------------------------------
    */

    if (
      typeof FormData !== "undefined" &&
      config.data instanceof FormData
    ) {
      /*
       * Remove any Content-Type inherited from defaults.
       * Axios/browser will generate it automatically.
       */
      if (config.headers) {
        delete config.headers["Content-Type"];
        delete config.headers["content-type"];
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/*
|--------------------------------------------------------------------------
| Response interceptor
|--------------------------------------------------------------------------
*/

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    if (error.response) {
      const status = error.response.status;

      /*
       * Do not redirect automatically here.
       * ProtectedRoute/AuthProvider should control authentication.
       */

      if (status === 401) {
        console.warn(
          "Authentication required."
        );
      }
    }

    return Promise.reject(error);
  }
);

/*
|--------------------------------------------------------------------------
| Error normalizer
|--------------------------------------------------------------------------
*/

function normalizeError(error) {
  /*
   * ---------------------------------------------------------------
   * Timeout
   * ---------------------------------------------------------------
   *
   * Axios timeout errors can also contain `request`.
   *
   * Therefore timeout MUST be checked before `error.request`.
   *
   * Previously a timeout was incorrectly reported as:
   *
   * "Unable to reach the CareerForge backend."
   *
   * even when Core Backend was simply taking longer to respond.
   */

  if (
    error?.code === "ECONNABORTED" ||
    error?.code === "ETIMEDOUT" ||
    error?.message?.toLowerCase?.().includes("timeout")
  ) {
    return new Error(
      "The CareerForge AI request is taking longer than expected. Please try again."
    );
  }

  /*
   * ---------------------------------------------------------------
   * Backend returned an HTTP response
   * ---------------------------------------------------------------
   */

  if (error?.response) {
    const data = error.response.data;

    let message =
      data?.message ||
      data?.detail ||
      data?.error;

    /*
     * FastAPI validation errors
     */
    if (!message && Array.isArray(data?.detail)) {
      message = data.detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          return (
            item?.msg ||
            "Validation error"
          );
        })
        .join(", ");
    }

    return new Error(
      message ||
        `Request failed with status ${error.response.status}`
    );
  }

  /*
   * ---------------------------------------------------------------
   * Browser sent the request but received no response
   * ---------------------------------------------------------------
   */

  if (error?.request) {
    return new Error(
      "Unable to reach the CareerForge backend."
    );
  }

  /*
   * ---------------------------------------------------------------
   * Unknown client-side error
   * ---------------------------------------------------------------
   */

  return new Error(
    error?.message ||
      "An unexpected error occurred."
  );
}

/*
|--------------------------------------------------------------------------
| API Client
|--------------------------------------------------------------------------
*/

class ApiClient {
  async get(url, config = {}) {
    try {
      const response = await api.get(
        url,
        config
      );

      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async post(
    url,
    data = undefined,
    config = {}
  ) {
    try {
      const response = await api.post(
        url,
        data,
        config
      );

      /*
       * Return the actual backend response body.
       */
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async put(
    url,
    data = undefined,
    config = {}
  ) {
    try {
      const response = await api.put(
        url,
        data,
        config
      );

      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async patch(
    url,
    data = undefined,
    config = {}
  ) {
    try {
      const response = await api.patch(
        url,
        data,
        config
      );

      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async delete(url, config = {}) {
    try {
      const response = await api.delete(
        url,
        config
      );

      /*
       * DELETE 204 has no response body.
       */
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  /*
  |--------------------------------------------------------------------------
  | Multipart upload
  |--------------------------------------------------------------------------
  */

  async upload(
    url,
    formData,
    onProgress = undefined
  ) {
    try {
      /*
       * IMPORTANT:
       * No Content-Type header here.
       *
       * Browser creates the multipart boundary.
       */

      const response = await api.post(
        url,
        formData,
        {
          onUploadProgress: (event) => {
            if (
              !onProgress ||
              !event.total
            ) {
              return;
            }

            const percentage = Math.round(
              (event.loaded * 100) /
                event.total
            );

            onProgress(percentage);
          },
        }
      );

      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }
}

const apiClient = new ApiClient();

export default apiClient;