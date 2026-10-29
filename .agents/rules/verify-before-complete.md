# Verification Before Completion Rule

Whenever code modifications are made to `swarna_khata_book`:

1. **Mandatory Full-Suite Verification**:
   - Before declaring any feature or bug fix complete, execute the regression check:
     ```powershell
     .\scripts\verify_all_features.ps1
     ```
   - Ensure that:
     - Frontend builds with zero TypeScript errors (`tsc -b`).
     - Backend regression tests pass 100% (`manage.py test tests --keepdb`).
     - Playwright browser E2E tests pass without timeouts.

2. **Zero Regression Tolerance**:
   - If a test fails, do NOT declare the task complete or hide the error. Immediately debug and fix the regression before returning your response to the user.

3. **Status Reporting**:
   - Include a concise Feature Health Matrix summary in your final response confirming that all core modules remain fully operational.

4. **Keep Knowledge Graph Current**:
   - Run `graphify update .` after any code modification.
