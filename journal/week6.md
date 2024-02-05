# Week 6 — Deploying Containers
In this week, I started with understanding about NAT - it take IP addresses and maps to external one. It allows a way to talk safely out of Internet. For instance : Private IP to Public IP. 

Created a HealthCheck script for RDS connection and added in `backend-flask/bin/db/test`

Also created cloudwatch groups for `cruddur` cluster
```
aws logs create-log-group --log-group-name cruddur
aws logs put-retention-policy --log-group-name cruddur --retention-in-days 1
```

And decided to have three repositories (Amazon image env frame)  :
1. Base image for Python 
2. One for Flask
3. and the third for React

//TODO
