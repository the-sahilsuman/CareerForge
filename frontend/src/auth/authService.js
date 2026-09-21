import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from "amazon-cognito-identity-js";

const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID;
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;

if (!userPoolId || !clientId) {
  throw new Error(
    "Cognito configuration is missing. Check frontend/.env"
  );
}

const userPool = new CognitoUserPool({
  UserPoolId: userPoolId,
  ClientId: clientId,
});


/*
|--------------------------------------------------------------------------
| Register
|--------------------------------------------------------------------------
*/

export function register({
  username,
  email,
  password,
}) {
  return new Promise((resolve, reject) => {
    const emailAttribute = new CognitoUserAttribute({
      Name: "email",
      Value: email,
    });

    const nameAttribute = new CognitoUserAttribute({
      Name: "name",
      Value: username,
    });

    userPool.signUp(
      username,
      password,
      [emailAttribute, nameAttribute],
      [],
      (error, result) => {
        if (error) {
          console.error("COGNITO REGISTER ERROR:", error);
          console.error("MESSAGE:", error.message);
          console.error("CODE:", error.code);
          console.error("NAME:", error.name);

          reject(error);
          return;
        }

        resolve(result);
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Confirm email
|--------------------------------------------------------------------------
*/

export function confirmRegistration({
  username,
  code,
}) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({
      Username: username,
      Pool: userPool,
    });

    user.confirmRegistration(
      code,
      true,
      (error, result) => {
        if (error) {
          reject(error);
          return;
        }

        resolve(result);
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Login
|--------------------------------------------------------------------------
*/

export function login({
  username,
  password,
}) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({
      Username: username,
      Pool: userPool,
    });

    const authenticationDetails =
      new AuthenticationDetails({
        Username: username,
        Password: password,
      });

    user.authenticateUser(
      authenticationDetails,
      {
        onSuccess: (session) => {
          resolve(session);
        },

        onFailure: (error) => {
          reject(error);
        },

        newPasswordRequired: (
          userAttributes,
          requiredAttributes
        ) => {
          resolve({
            challenge: "NEW_PASSWORD_REQUIRED",
            user,
            userAttributes,
            requiredAttributes,
          });
        },
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Current Cognito user
|--------------------------------------------------------------------------
*/

export function getCurrentUser() {
  return userPool.getCurrentUser();
}


/*
|--------------------------------------------------------------------------
| Current session
|--------------------------------------------------------------------------
*/

export function getSession() {
  return new Promise((resolve, reject) => {
    const user = userPool.getCurrentUser();

    if (!user) {
      reject(
        new Error("No authenticated user")
      );
      return;
    }

    user.getSession(
      (error, session) => {
        if (error) {
          reject(error);
          return;
        }

        if (
          !session ||
          !session.isValid()
        ) {
          reject(
            new Error(
              "Session is invalid or expired"
            )
          );
          return;
        }

        resolve(session);
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| User role
|--------------------------------------------------------------------------
*/

export async function getUserRole() {
  try {
    const session = await getSession();

    const payload = session
      .getIdToken()
      .decodePayload();

    const groups =
      payload["cognito:groups"] || [];

    if (groups.includes("ADMIN")) {
      return "ADMIN";
    }

    if (groups.includes("SUPER_ADMIN")) {
      return "HR";
    }

    return "SUPER_ADMIN";

  } catch (error) {
    console.error(
      "Unable to get user role:",
      error
    );

    return null;
  }
}


/*
|--------------------------------------------------------------------------
| ID token
|--------------------------------------------------------------------------
*/

export async function getIdToken() {
  const session = await getSession();

  return session
    .getIdToken()
    .getJwtToken();
}


/*
|--------------------------------------------------------------------------
| Access token
|--------------------------------------------------------------------------
*/

export async function getAccessToken() {
  const user = getCurrentUser();

  if (!user) {
    return null;
  }

  return new Promise((resolve, reject) => {
    user.getSession((error, session) => {
      if (error) {
        reject(error);
        return;
      }

      if (!session?.isValid()) {
        resolve(null);
        return;
      }

      resolve(session.getAccessToken().getJwtToken());
    });
  });
}


/*
|--------------------------------------------------------------------------
| Logout
|--------------------------------------------------------------------------
*/

export function logoutUser() {
  const user = userPool.getCurrentUser();

  if (user) {
    user.signOut();
  }
}


/*
|--------------------------------------------------------------------------
| Resend verification code
|--------------------------------------------------------------------------
*/

export function resendConfirmationCode({
  username,
}) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({
      Username: username,
      Pool: userPool,
    });

    user.resendConfirmationCode(
      (error, result) => {
        if (error) {
          reject(error);
          return;
        }

        resolve(result);
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Forgot password
|--------------------------------------------------------------------------
*/

export function forgotPassword({
  username,
}) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({
      Username: username,
      Pool: userPool,
    });

    user.forgotPassword({
      onSuccess: (result) => {
        resolve(result);
      },

      onFailure: (error) => {
        reject(error);
      },
    });
  });
}


/*
|--------------------------------------------------------------------------
| Confirm forgot password
|--------------------------------------------------------------------------
*/

export function confirmForgotPassword({
  username,
  code,
  newPassword,
}) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({
      Username: username,
      Pool: userPool,
    });

    user.confirmPassword(
      code,
      newPassword,
      {
        onSuccess: () => {
          resolve(true);
        },

        onFailure: (error) => {
          reject(error);
        },
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Change password
|--------------------------------------------------------------------------
*/

export function changeTemporaryPassword({
  oldPassword,
  newPassword,
}) {
  return new Promise((resolve, reject) => {
    const user =
      userPool.getCurrentUser();

    if (!user) {
      reject(
        new Error("No authenticated user")
      );
      return;
    }

    user.getSession(
      (sessionError, session) => {
        if (sessionError) {
          reject(sessionError);
          return;
        }

        if (
          !session ||
          !session.isValid()
        ) {
          reject(
            new Error(
              "Session is invalid or expired"
            )
          );
          return;
        }

        user.changePassword(
          oldPassword,
          newPassword,
          (error, result) => {
            if (error) {
              reject(error);
              return;
            }

            resolve(result);
          }
        );
      }
    );
  });
}


/*
|--------------------------------------------------------------------------
| Export
|--------------------------------------------------------------------------
*/

export { userPool };