# Week 8 — Serverless Image Processing
## Implement CDK Stack

- npm install aws-cdk -g

- in .gitpod.yml

```yml
- name: cdk
    before: |
      npm install aws-cdk -g
```

- Use `cdk synth` to check cdk file before deploying it

- Run the cdk bootstrap command to configure our account for CDK

```sh
gitpod /workspace/aws-bootcamp-cruddur-2023/thumbing-serverless-cdk (main) $ cdk bootstrap "aws://632626636018/ca-central-1"
 ⏳  Bootstrapping environment aws://632626636018/ca-central-1...
Trusted accounts for deployment: (none)
Trusted accounts for lookup: (none)
Using default execution policy of 'arn:aws:iam::aws:policy/AdministratorAccess'. Pass '--cloudformation-execution-policies' to customize.
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://632626636018/ca-central-1 bootstrapped.
 ```

 - Use `cdk deploy` to deploy the CDK stack to AWS

 - Create `.env.example` to create env variables for CDK

 `cp .env.example .env` inside .gitpod.yml. This is because .env is ignored with our gitignore

 ```yml
THUMBING_BUCKET_NAME="assets.mycruddur.net"
THUMBING_FUNCTION_PATH="/workspace/aws-bootcamp-cruddur-2023/aws/lambdas/process-images/"
THUMBING_S3_FOLDER_INPUT="avatars/original"
THUMBING_S3_FOLDER_OUTPUT="avatars/processed"
THUMBING_WEBHOOK_URL="api.mycruddur.net/webhooks/avatar"
THUMBING_TOPIC_NAME="cruddur-assets"
```
