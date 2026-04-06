# Dynamic Subagent Routing Plan

## Context
- Need CLI feature to auto route user prompts to subagents by auto-detecting whether they should run.
- Decision-complete plan from earlier includes router, integration, hidden hint.

## Implementation Steps
1. Extend `subagents.py` metadata and loader:
   - Allow optional `triggers` alias list in YAML frontmatter and load into `SubagentMetadata`.
   - Ensure existing validation still requires name/description.
2. Add new router module:
   - `SubagentRouter` loads all candidates (local + `load_async_subagents`) and supports `select_for_prompt(prompt)` returning optional hint (subagent name, description, reason).
   - Matching via name/alias presence or keyword overlaps (configurable threshold). No LLM needed.
3. Integrate into CLI flow:
   - Add settings toggles/environment variable controlling auto routing.
   - Instantiate router in `app.py`, call before sending user prompts, and if a hint exists add UI notification and pass hint via `message_kwargs` to `_send_to_agent` and `execute_task_textual`.
   - Ensure UI shows hint message but main agent path unaffected if ignored.
4. Hidden assistant hint injection:
   - Update `execute_task_textual` to accept new `subagent_hint` arg and prepend hidden assistant message containing instructions for `subagent_type` and rationale.

## Testing
- Unit tests for router (keyword/alias/button matching, async inclusion).
- Tests ensuring `execute_task_textual` injects hidden message.
- Test verifying `_handle_user_message` passes hint via `message_kwargs`.

## Assumptions
- Keyword/alias heuristics suffice.
- Hidden hint is not user-visible.
- SubAgentMiddleware already exposes task tool.
