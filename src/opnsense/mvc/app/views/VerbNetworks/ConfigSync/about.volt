
<div class="alert alert-info hidden" role="alert" id="responseMsg"></div>

<div  class="col-md-12">
    <h1>Configuration Sync Log File</h1>

    <pre>
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::BUCKET_NAME"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:PutObject",
                "s3:GetObject",
            ],
            "Resource": [
                "arn:aws:s3:::BUCKET_NAME/PATH_IN_BUCKET/*"
            ]
        }
    ]
}
    </pre>

</div>
