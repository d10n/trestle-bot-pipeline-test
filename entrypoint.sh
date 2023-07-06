#!/bin/bash

set -eu

# Manage newest git versions (related to CVE https://github.blog/2022-04-12-git-security-vulnerability-announced/)
#
if [ -z ${GITHUB_WORKSPACE+x} ]; then
  echo "Setting git safe.directory default: /github/workspace ..."
  git config --global --add safe.directory /github/workspace
else
  echo "Setting git safe.directory GITHUB_WORKSPACE: $GITHUB_WORKSPACE ..."
  git config --global --add safe.directory "$GITHUB_WORKSPACE"
fi

if [ -z ${INPUT_REPOSITORY+x} ]; then
    echo "Skipping setting working directory as safe directory"
else
   echo "Setting git safe.directory default: $INPUT_REPOSITORY..."
   git config --global --add safe.directory "$INPUT_REPOSITORY"
fi

exec 3>&1

trap exec 3>&- EXIT


# Initialize the command variable
command="python3.8 -m trestlebot \
        --markdown-path=\"${INPUT_MARKDOWN_PATH}\" \
        --oscal-model=\"${INPUT_OSCAL_MODEL}\" \
        --ssp-index-path=\"${INPUT_SSP_INDEX_PATH}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
        --branch=\"${INPUT_BRANCH}\" \
        --file-patterns=\"${INPUT_FILE_PATTERN}\" \
        --committer-name=\"${INPUT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_COMMIT_AUTHOR_EMAIL}\" \
        --working-dir=\"${INPUT_REPOSITORY}\" \
        --skip-items=\"${INPUT_SKIP_ITEMS}\""

# Conditionally include flags
if [[ ${INPUT_SKIP_ASSEMBLE} == true ]]; then
    command+=" --skip-assemble"
fi

if [[ ${INPUT_SKIP_REGENERATE} == true ]]; then
    command+=" --skip-regenerate"
fi

if [[ ${INPUT_CHECK_ONLY} == true ]]; then
    command+=" --check-only"
fi

output=$(eval "$command" 2>&1 > >(tee /dev/fd/3))


commit=$(echo "$output" | grep "Commit Hash:" | sed 's/.*: //')

if [ -n "$commit" ]; then
    echo "changes=true" >> "$GITHUB_OUTPUT"
    echo "commit=$commit" >> "$GITHUB_OUTPUT"
else
    echo "changes=false" >> "$GITHUB_OUTPUT"
fi