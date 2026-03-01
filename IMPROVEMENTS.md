
### [FRONTEND] The WebSocket error handling currently logs errors to the application's main log
- **Priority:** medium
- **Observation:** The WebSocket error handling currently logs errors to the application's main log feed for user notification. This is functional but not ideal for immediate, prominent user feedback.
- **Suggested action:** Implement a dedicated toast notification system (e.g., using a library like react-toastify or a custom component) to display critical WebSocket connection errors to the user in a more prominent and less intrusive way.
- **Logged by:** task `375591c5` / agent `6bcf2b54` at 2026-02-27 22:28 UTC
