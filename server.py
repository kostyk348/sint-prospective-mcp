from mcp.server.fastmcp import FastMCP
from config import NAME, VERSION
from prospective import IntentionStack, MarkerStore, Persistence, ResumeEngine

mcp = FastMCP(NAME, version=VERSION)

stack = IntentionStack()
markers = MarkerStore()
persist = Persistence(stack, markers)
resume_engine = ResumeEngine(stack, markers)


@mcp.tool()
def prospective_push(intent: str, status: str = "active", context: str = "", parent_id: str = "") -> str:
    intention = stack.push(intent, context)
    return (
        f"Pushed intention [{intention.id}]: {intent}\n"
        f"  depth={intention.depth}, status={intention.status}\n"
        f"  context={context}"
    )


@mcp.tool()
def prospective_pop(intent_id: str) -> str:
    intention = stack.pop(intent_id)
    if intention is None:
        return f"Intention {intent_id} not found."
    persist.save()
    return f"Completed intention [{intention.id}]: {intention.intent}"


@mcp.tool()
def prospective_suspend(intent_id: str, reason: str) -> str:
    intention = stack.suspend(intent_id, reason)
    if intention is None:
        return f"Intention {intent_id} not found."
    persist.save()
    return f"Suspended intention [{intention.id}]: {intention.intent}\n  reason: {reason}"


@mcp.tool()
def prospective_resume() -> str:
    result = resume_engine.resume()
    if not result["has_pending"]:
        return "No pending intentions. Nothing to resume."

    lines = [
        result["message"],
        "",
        "Top active intention:",
        f"  [{result['top_active_intent']['id']}] {result['top_active_intent']['intent']}",
        f"  context: {result['top_active_intent']['context']}",
        f"  depth: {result['top_active_intent']['depth']}",
        f"  created: {result['top_active_intent']['created_at']}",
        f"  idle: {result['time_since_active_seconds']}s",
    ]

    if result["history_summary"]:
        lines.append("")
        lines.append("Intention stack:")
        for h in result["history_summary"]:
            indent = "  " * h["depth"]
            lines.append(f"  {indent}[{h['id']}] {h['intent']} ({h['status']})")

    if result["context_markers"]:
        lines.append("")
        lines.append("Context markers:")
        for m in result["context_markers"]:
            lines.append(f"  #{m['position']}: {m['note']}")

    return "\n".join(lines)


@mcp.tool()
def prospective_list(status_filter: str = "") -> str:
    intentions = stack.list(status_filter if status_filter else None)
    if not intentions:
        return "No intentions found."
    lines = [f"{'ID':<14} {'INTENT':<40} {'STATUS':<12} {'DEPTH':<6}", "-" * 72]
    for i in intentions:
        intent_trunc = i.intent[:38] + ".." if len(i.intent) > 38 else i.intent
        lines.append(f"{i.id:<14} {intent_trunc:<40} {i.status:<12} {i.depth:<6}")
    return "\n".join(lines)


@mcp.tool()
def prospective_marker(position: int, note: str) -> str:
    marker = markers.add(position, note)
    return f"Marker [{marker.id}] at position {position}: {note}"


@mcp.tool()
def prospective_snapshot() -> str:
    snapshot_id = stack.snapshot()
    path = persist.save()
    return f"Snapshot [{snapshot_id}] saved to {path}"


@mcp.tool()
def prospective_restore(snapshot_id: str) -> str:
    if stack.restore(snapshot_id):
        return f"Restored snapshot [{snapshot_id}]."
    # Try loading from disk
    if persist.load():
        return "Restored from last persisted state."
    return f"Snapshot {snapshot_id} not found."


def main():
    mcp.run()


if __name__ == "__main__":
    main()
