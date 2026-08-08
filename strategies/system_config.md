### VERIFICATION STRATEGY: SYSTEM CONFIGURATIONS & AUTOMATION
1. **Environment Compatibility:** Verify compatibility with the specified OS (Arch Linux / Windows 11 / Android). If commands or paths depend on an unspecified environment, demand clarification via `missing_info`.
2. **Execution Safety:** Look for potentially destructive commands, nonexistent system paths, and process conflicts (e.g., GUI in Session 0, background services, port bindings).
3. **Operational Order:** Are prerequisites clearly stated? What must the user verify BEFORE running the configuration?
4. **Idempotency:** Is it safe to run this script or configuration repeatedly on a daily basis?
