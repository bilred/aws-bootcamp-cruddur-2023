# Week 0 — Billing and Architecture

Install AWS CLI
'tasks:
    - name: aws-cli
      env:
        AWS_CLI_AUTO_PROMPET: on-partial
     init:
        cd /workspece
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        cd $THETA_WORKSPACE_ROOT'