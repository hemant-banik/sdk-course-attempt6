"""REFERENCE SOLUTION — Step 21: Bedrock and Vertex client variants

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice21_bedrock_vertex.py
Graded by:                        .github/scripts/check_step21.py

To use: copy this file to exercises/practice21_bedrock_vertex.py, then run
    python exercises/practice21_bedrock_vertex.py
"""

from anthropic import AnthropicBedrock, AnthropicVertex

# --- AWS Bedrock ---
# Use AnthropicBedrock when your team already runs infrastructure on AWS
# and wants Claude usage billed/governed through that existing AWS account
# (IAM roles, VPC boundaries, AWS cost reporting) rather than a separate
# Anthropic API key. Auth comes from AWS credentials (access key/secret
# key or an IAM role), not an Anthropic API key.
bedrock_client = AnthropicBedrock(
    aws_access_key="fake-access-key-for-practice",
    aws_secret_key="fake-secret-key-for-practice",
    aws_region="us-west-2",
)

# --- Google Cloud Vertex AI ---
# Use AnthropicVertex when your team already runs infrastructure on GCP
# and wants Claude usage billed/governed through that existing GCP project
# via Vertex AI, using gcloud application-default credentials instead of
# an Anthropic API key.
vertex_client = AnthropicVertex(
    project_id="fake-project-for-practice",
    region="global",
)

print("Bedrock client:", type(bedrock_client).__name__)
print("Vertex client:", type(vertex_client).__name__)
print("Same .messages.create(...) call shape works on both — only the constructor differs.")
