# Week 6 — Deploying Containers
In this week, I started with understanding about NAT - it take IP addresses and maps to external one. It allows a way to talk safely out of Internet. For instance : Private IP to Public IP. 

Created a HealthCheck script for RDS connection and added in `backend-flask/bin/db/test`

Also created cloudwatch groups for `cruddur` cluster
```
aws logs create-log-group --log-group-name cruddur
aws logs put-retention-policy --log-group-name cruddur --retention-in-days 1
```

## Gaining Access to ECS Fargate Container
## Create ECR repo and push image
And decided to have three repositories (Amazon image env frame)  :
1. Base image for Python 
2. One for Flask
3. and the third for React

Basically what we can do now is Stroe our container in ECR and remove the single point of failure (related to using Docker Hub)
In the end, replace the URL that the image comes FROM with the one we created in ECR

### Login to ECR
By using the docker login to be able to push a new image
```sh
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

### For Base-image python
create an empty private repository named `cruddur-python`
```sh
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```

#### Set URL
ECR URL mapping for Python
```sh
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
echo $ECR_PYTHON_URL
```

#### Pull Image

```sh
docker pull python:3.10-slim-buster
```

#### Tag Image

```sh
docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster
```

#### Push Image

```sh
docker push $ECR_PYTHON_URL:3.10-slim-buster
```
Then I edited `Dockerfile` with ECR URL and also did Health-Check

**Creating Repo for Flask**
Create Repo
```sh
aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE
```
  
  Set URL
```sh
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL
```

Build Image
```sh
docker build -t backend-flask .
```

Tag Image
```sh
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest
```

Push Image
```sh
docker push $ECR_BACKEND_FLASK_URL:latest
```

This was for the Backend and then created for Frontend as well

**For Frontend**
created Repo
```sh
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```
  
Set URL 
```sh
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```

Build Image for Frontend 
```sh
docker build \
--build-arg REACT_APP_BACKEND_URL="https://4567-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="$REACT_APP_AWS_USER_POOLS_ID" \
--build-arg REACT_APP_CLIENT_ID="$REACT_APP_CLIENT_ID" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```
**Note: If this build script doesn't works like this then ad a period infront of `docker build . \`. This will state that you have to build the image in the present directory on which you ae running the command.**

Tag Image 
```sh
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
```

Push Image
```sh
docker push $ECR_FRONTEND_REACT_URL:latest
```

