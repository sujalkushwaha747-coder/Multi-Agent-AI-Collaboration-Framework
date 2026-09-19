import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PromptForm } from "./PromptForm";

describe("PromptForm", () => {
  it("submits a prompt and task category", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<PromptForm documents={[]} isRunning={false} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Prompt"), "Explain RAG.");
    await user.click(screen.getByRole("button", { name: /run comparison/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      prompt: "Explain RAG.",
      task_category: "academic",
      document_ids: [],
      reference_answer: null
    });
  });
});

