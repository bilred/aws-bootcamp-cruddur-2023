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

Creat the forlder build to use it in frontend docker image, including the nginx.conf (reverse proxy as ligthweight http server) 
```sh
npm run build
```

Build Image for Frontend 
Note: when we used the load-balancer the BACKEND_URL will be our Load balancer address in my case is "http://cruddur-alb-472351043.ca-central-1.elb.amazonaws.com:4567"
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

## Register Task Defintions
### Create Task and Exection Roles for Task Defintion
Passing Senstive Data to Task Defintion
#### Create ExecutionRole

```sh
aws iam create-role \    
--role-name CruddurServiceExecutionPolicy  \   
--assume-role-policy-document file://aws/policies/service-assume-role-execution-policy.json
```

```sh
aws iam put-role-policy \
  --policy-name CruddurServiceExecutionPolicy \
  --role-name CruddurServiceExecutionRole \
  --policy-document file://aws/policies/service-execution-policy.json
"
```

### Passing Senstive Data to Task Defintion
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-ssm-paramstore.html

```sh
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```

#### Create TaskRole

```sh
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"

aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}
"

aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```

**Set Defaults Var**
```sh
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```

```sh
export DEFAULT_SUBNET_IDS=$(aws ec2 describe-subnets  \
 --filters Name=vpc-id,Values=$DEFAULT_VPC_ID \
 --query 'Subnets[*].SubnetId' \
 --output json | jq -r 'join(",")')
echo $DEFAULT_SUBNET_IDS
```

Yes, now we can create our Register Task Defintion! after all attached permission
For Backend
```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```
For Frontend
```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json
```
Created Role Policies for these services and created a Task Role and attached that to Policies for CloudWatch and X-RAY.

After created the task definition we can create the service 
**Create Services** in the cluster cruddur

```sh
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```

```sh
aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json
```

## Debug Utility
Connect to the container (with task id only in the cluster)
To access form gitpod ubuntu install the Systems-Manager 
https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-debian-and-ubuntu.html
```sh
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task e4432ccece1a45da90e6c0474baefe91 \
--container backend-flask \
--command "/bin/bash" \
--interactive
```

Why we got this erreor message? (let see in the container) 
```
Task stopped at: 2024-02-08T22:30:54.032Z
ResourceInitializationError: unable to pull secrets or registry auth: execution resource retrieval failed: unable to retrieve ecr registry auth: service call has been retried 1 time(s): AccessDeniedException: User: arn:aws:sts::873001202713:assumed-role/CruddurServiceExecutionRole/c83b2ce015f240a6ad668177d60c2f38 is not authorized to perform: ecr:GetAuthorizationToken on resource: * because no identity-based policy allows the ecr:GetAuthorizationToken action status code: 400, request id: 66372395-f40d-41c3-8cf2-a18a60167fab
```