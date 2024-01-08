# Week 3 — Decentralized Authentication

## Install AWS Amplify

```sh
npm i aws-amplify --save
```

## The Goal of implementation
Using aws-amplify without amplify-ui to build an authentication with JWT token including (sign-in, sign-up, signout, confirmation code by email) on the client side (react.js) and need to validate token (from the request) backend side (flask-backend) 

## Via AWS Cognito (manual creation)
Using the AWS Console we'll create a Cognito User Group

## Configure Amplify
We need to hook up our cognito pool to our code in the `App.js`

```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,      // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```

For testing purposes the sign-in page before implementing the sign-up and confirming, we do the user creation manually 
```sh
aws cognito-idp admin-set-user-password \
  --user-pool-id <your-user-pool-id> \
  --username <username> \
  --password <password> \
  --permanent
```

## Conditionally show components based on logged in or logged out

Update the `HomeFeedPage.js`
Update the `DesktopNavigation.js` 
Update the `ProfileInfo.js` (Notice we are passing the user)
Update the `DesktopSidebar.js` (so that it conditionally shows components in case you are logged in or not.)
Update the `Signin.js` (onsubmit)
Update the `Signup.js` (onsubmit)
Update the `Confirmation.js` (resend_code and onsubmit)
Update the `Recovery.js` (onsubmit_send_code and onsubmit_confirm_code)
See my Commits on Jan 3 to Jan 7, 2024 (for front-end and back-end implementation)

## Authenticating Server Side
Add in the `HomeFeedPage.js` a header pass along the access token (from localStorage comes with aws-cognito)
```js
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  }
```

Add in the `sign-out.js`
```js
localStorage.removeItem("access_token")
```

In the `app.py`
```py
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

NB: Architecture Design?, why use the coupling library instead of SideCar Architecture OR GatewayAPI with AWS Lambda
// TODO add some napkin design
