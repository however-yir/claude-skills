# Java Full-Stack Checklist

## Before Editing

- Confirm the affected module, route, service, mapper, and schema surface.
- Check whether the problem is logic, contract, data, performance, or test coverage.
- Look for existing patterns before introducing a new one.

## While Changing

- Keep controller, service, repository, and DTO boundaries explicit.
- Prefer small, reviewable diffs over broad cleanups.
- Preserve backward compatibility unless the task explicitly allows breaking changes.
- For SQL changes, verify indexes, filters, sorts, and join costs.

## Before Closing

- Compile or run the narrowest relevant test target if available.
- Verify edge cases and error paths.
- Summarize user-visible behavior, technical rationale, and residual risks.
