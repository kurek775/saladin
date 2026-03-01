#!/bin/bash

set -euo pipefail

WORKSPACE_DIR="backend/workspace"
TODO_APP_TEMPLATE_DIR="backend/todo-app-template"

function clean_workspace() {
    echo "Cleaning workspace: ${WORKSPACE_DIR}"
    # Remove all contents but keep the directory itself
    find "${WORKSPACE_DIR}" -mindepth 1 -delete
    mkdir -p "${WORKSPACE_DIR}" # Ensure it exists if it was completely removed
}

function init_todo_app() {
    echo "Initializing workspace with todo-app template."
    if [ ! -d "${TODO_APP_TEMPLATE_DIR}" ]; then
        echo "Error: Todo-app template directory not found at ${TODO_APP_TEMPLATE_DIR}"
        exit 1
    fi # Corrected: 'fi' instead of '}'
    mkdir -p "${WORKSPACE_DIR}/todo-app" # Ensure the target directory exists
    cp -r "${TODO_APP_TEMPLATE_DIR}/." "${WORKSPACE_DIR}/todo-app/" # Copy contents
    echo "Todo-app template copied to ${WORKSPACE_DIR}/todo-app"
}

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 --clean | --init-todo-app"
    exit 1
fi

case "$1" in
    --clean)
        clean_workspace
        ;;
    --init-todo-app)
        clean_workspace
        init_todo_app
        ;;
    *)
        echo "Invalid option: $1"
        echo "Usage: $0 --clean | --init-todo-app"
        exit 1
        ;;
esac

echo "Workspace operation complete."
