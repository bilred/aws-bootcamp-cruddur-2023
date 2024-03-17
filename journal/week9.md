# Week 9 — CI/CD with CodePipeline, CodeBuild and CodeDeploy

## Configuring CodeBuild Part 1 and 2

I created a `buildspec.yml` file inside `backend-flask/` with the contents below:

```yml
# Buildspec runs in the build stage of your pipeline.
version: 0.2
phases:
  install:
    runtime-versions:
      docker: 20
    commands:
      - echo "cd into $CODEBUILD_SRC_DIR/backend"
      - cd $CODEBUILD_SRC_DIR/backend-flask
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $IMAGE_URL
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t backend-flask .
      - "docker tag $REPO_NAME $IMAGE_URL/$REPO_NAME"
      - echo "Creating imagedefinitions.json"
      - cd $CODEBUILD_SRC_DIR
      - printf "[{\"name\":\"$CONTAINER_NAME\",\"imageUri\":\"$IMAGE_URL/$REPO_NAME\"}]" > imagedefinitions.json

  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image..
      - docker push $IMAGE_URL/$REPO_NAME

env:
  variables:
    AWS_ACCOUNT_ID: 873001202713
    AWS_DEFAULT_REGION: ca-central-1
    CONTAINER_NAME: backend-flask
    IMAGE_URL: 873001202713.dkr.ecr.ca-central-1.amazonaws.com
    REPO_NAME: backend-flask:latest
artifacts:
  files:
    - imagedefinitions.json
```

Then using the AWS Console, in _CodeBuild_ I created a CodeBuild Project called *cruddur-backend-flask-bake-image*.

The build watched the `prod` branch of my github project. 
I forced the build, but the build failed due to permission errors with ECR. 

```sh
error occurred (AccessDeniedException) when calling the GetAuthorizationToken operation: User: arn:aws:sts::632626636018:assumed-role/codebuild-cruddur-backend-flask-bake-image-service-role/AWSCodeBuild-6ec3b5c8-64e6-4817-a8a4-967d9bb1e653 is not authorized to perform: ecr:GetAuthorizationToken on resource: * because no identity-based policy allows the ecr:GetAuthorizationToken action
Error: Cannot perform an interactive login from a non TTY device
```

To fix this error I needed to create an inline IAM policy, for the current CodeBuild IAM Role called `codebuild-cruddur-backend-flask-bake-image-service-role`.

Here is the inline policy that I added:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CompleteLayerUpload",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ],
            "Resource": [
                "arn:aws:ecr:ca-central-1:873001202713:repository/backend-flask"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Resource": "*"
        }
    ]
}
```
With the new inline IAM policy, I was able to successfully run the CodeBuild.

![codebuild_successful](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/codebuild_successful.png)

I verified in ECR that a new image was pushed to it.

![codebuild_pushed_image_to_ECR](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/codebuild_pushed_image_to_ECR.png)

## Configuring CodePipeline

Using CodePipeline I created a new pipeline called `cruddur-backend-fargate`.

- The pipeline uses `https://github.com/poxrud/aws-bootcamp-cruddur-2023` as source, and watches the `prod` branch to trigger the pipeline. 
- The next step in the pipeline is the `Build` step and it uses the *CodeBuild* project that was already created above. 
- The final step of the Pipeline is the `Deploy` step. This step triggers a deploy to our *cruddur* ECS cluster.

Here is me successfully triggering the Pipeline.

![codepipeline_successful](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/codepipeline_successful.png)

I then tested the API endpoint at `https://api.mycruddur.net/api/health-check`

![health_check_after_build](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/health_check_after_build.png)

Finally, in order to validate that the Pipeline can trigger on changes to prod and deploy I changed the `/api/health-check` endpoint
to return the version number of the healthcheck.

In `backend-flask/app.py`

```py
@app.route('/api/health-check')
def health_check():
  return {'success': True, 'version': 2}, 200
```

I pushed these changes to `prod`, which triggered a new Pipeline

![prod_push_trigger](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/prod_push_trigger.png)

Finally I checked the new API health-check endpoint on `https://api.mycruddur.net/api/health-check`

![health_check_after_prod_push.png](https://github.com/poxrud/aws-bootcamp-cruddur-2023/raw/main/assets/health_check_after_prod_push.png)

