#!/usr/bin/env bash
set -euo pipefail

OWNER="${1:-sameerkhanna786}"
REPO="${2:-project_trampoline_pong}"
BRANCH="${3:-main}"
POLICY_FILE="${4:-.github/main-branch-protection.json}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required."
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Error: GitHub CLI is not authenticated."
  echo "Run: gh auth login -h github.com"
  exit 1
fi

if [ ! -f "${POLICY_FILE}" ]; then
  echo "Error: policy file not found: ${POLICY_FILE}"
  exit 1
fi

echo "Applying branch protection policy to ${OWNER}/${REPO}:${BRANCH}..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --input "${POLICY_FILE}" >/dev/null

echo "Policy applied. Verifying key settings..."
gh api \
  -H "Accept: application/vnd.github+json" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --jq '{enforce_admins: .enforce_admins.enabled, required_pr_reviews: .required_pull_request_reviews.required_approving_review_count, code_owner_reviews: .required_pull_request_reviews.require_code_owner_reviews, push_restrictions: ((.restrictions.users // []) | map(.login))}'
