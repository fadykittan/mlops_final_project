# AWS Setup Guide for GitHub Actions CI/CD

This guide will help you set up AWS resources and configure GitHub Actions to automatically build and deploy your Docker image to AWS Lambda.

## Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository with Actions enabled
3. AWS CLI installed locally (for initial setup)

## Step 1: Create AWS Resources

### 1.1 Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
    --repository-name mlops-final-project \
    --region us-east-1

# Get the repository URI (you'll need this)
aws ecr describe-repositories \
    --repository-names mlops-final-project \
    --region us-east-1 \
    --query 'repositories[0].repositoryUri' \
    --output text
```

### 1.2 Create IAM User for GitHub Actions

```bash
# Create IAM user
aws iam create-user --user-name github-actions-mlops

# Create and attach policy for ECR and Lambda access
cat > github-actions-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionCode",
                "lambda:GetFunction",
                "lambda:ListFunctions"
            ],
            "Resource": "arn:aws:lambda:us-east-1:*:function:mlops-final-project*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name GitHubActionsMLOpsPolicy \
    --policy-document file://github-actions-policy.json

aws iam attach-user-policy \
    --user-name github-actions-mlops \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsMLOpsPolicy
```

### 1.3 Create Access Keys

```bash
# Create access keys for the IAM user
aws iam create-access-key --user-name github-actions-mlops
```

**Important**: Save the Access Key ID and Secret Access Key securely.

## Step 2: Create Lambda Function

### 2.1 Create Lambda Function (Container Image)

```bash
# Create Lambda function using container image
aws lambda create-function \
    --function-name mlops-final-project \
    --package-type Image \
    --code ImageUri=YOUR_ECR_URI:latest \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --timeout 300 \
    --memory-size 1024 \
    --region us-east-1
```

### 2.2 Create IAM Role for Lambda

```bash
# Create trust policy for Lambda
cat > lambda-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document file://lambda-trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

## Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add the following secrets:

### Required Secrets:

1. **AWS_ACCESS_KEY_ID**: The access key ID from Step 1.3
2. **AWS_SECRET_ACCESS_KEY**: The secret access key from Step 1.3
3. **LAMBDA_FUNCTION_NAME**: `mlops-final-project` (or your chosen function name)

### Optional Environment Variables:

You may also want to add these as repository secrets if your application needs them:

4. **GOOGLE_API_KEY**: For your Google API integration
5. **AWS_REGION**: `us-east-1` (if different from default)

## Step 4: Update Workflow Configuration

If you need to modify the workflow, update the following in `.github/workflows/deploy.yml`:

- **AWS_REGION**: Change if you're using a different region
- **ECR_REPOSITORY**: Change if you used a different repository name
- **LAMBDA_FUNCTION_NAME**: Update the secret name if different

## Step 5: Test the Workflow

1. Push your changes to the `main` or `master` branch
2. Go to Actions tab in your GitHub repository
3. Monitor the workflow execution
4. Check AWS Lambda console to verify the function was updated

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Ensure IAM user has correct permissions
2. **ECR Repository Not Found**: Verify repository name and region
3. **Lambda Update Failed**: Check function name and permissions
4. **Image Too Large**: Consider optimizing Docker image or increasing Lambda memory

### Useful Commands:

```bash
# Check ECR repositories
aws ecr describe-repositories --region us-east-1

# Check Lambda functions
aws lambda list-functions --region us-east-1

# Check IAM user policies
aws iam list-attached-user-policies --user-name github-actions-mlops
```

## Cost Optimization

- ECR charges for storage: Consider lifecycle policies to delete old images
- Lambda charges for execution time and memory: Monitor usage and optimize
- GitHub Actions: Free tier includes 2,000 minutes/month for private repos

## Security Best Practices

1. Use least privilege principle for IAM permissions
2. Rotate access keys regularly
3. Use AWS Secrets Manager for sensitive data
4. Enable CloudTrail for audit logging
5. Consider using OIDC instead of access keys for better security
