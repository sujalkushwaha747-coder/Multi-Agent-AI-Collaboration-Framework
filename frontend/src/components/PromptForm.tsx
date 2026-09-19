import { Loader2, Play, RefreshCw } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import type { DocumentRecord, TaskCategory } from "../types";

interface PromptFormProps {
  documents: DocumentRecord[];
  isRunning: boolean;
  onSubmit: (payload: {
    prompt: string;
    task_category: TaskCategory;
    document_ids: string[];
    reference_answer?: string | null;
  }) => Promise<void> | void;
}

const samplePrompts = [
  "Explain the concept of Retrieval-Augmented Generation and its advantages.",
  "Design a high-level architecture for an online library management system.",
  "Create an SRS outline for an online examination system."
];

export function PromptForm({ documents, isRunning, onSubmit }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");
  const [taskCategory, setTaskCategory] = useState<TaskCategory>("academic");
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [referenceAnswer, setReferenceAnswer] = useState("");
  const indexedDocuments = useMemo(
    () => documents.filter((document) => document.status === "indexed"),
    [documents]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      prompt,
      task_category: taskCategory,
      document_ids: selectedDocs,
      reference_answer: referenceAnswer.trim() || null
    });
  }

  function toggleDocument(id: string) {
    setSelectedDocs((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id]
    );
  }

  return (
    <form className="experimentForm" onSubmit={handleSubmit}>
      <label className="field">
        <span>Prompt</span>
        <textarea
          aria-label="Prompt"
          placeholder="Enter an academic or technical task..."
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          required
          maxLength={12000}
        />
      </label>

      <div className="sampleRow" aria-label="Sample prompts">
        {samplePrompts.map((sample) => (
          <button
            key={sample}
            type="button"
            className="ghostButton"
            onClick={() => setPrompt(sample)}
          >
            <RefreshCw size={14} />
            <span>{sample}</span>
          </button>
        ))}
      </div>

      <fieldset className="segmentedField">
        <legend>Task category</legend>
        {(["academic", "technical", "general"] as TaskCategory[]).map((category) => (
          <label key={category} className={taskCategory === category ? "segment active" : "segment"}>
            <input
              type="radio"
              name="taskCategory"
              value={category}
              checked={taskCategory === category}
              onChange={() => setTaskCategory(category)}
            />
            <span>{category}</span>
          </label>
        ))}
      </fieldset>

      <label className="field">
        <span>Reference answer</span>
        <textarea
          className="smallTextArea"
          aria-label="Reference answer"
          placeholder="Optional ground truth answer for accuracy scoring"
          value={referenceAnswer}
          onChange={(event) => setReferenceAnswer(event.target.value)}
          maxLength={20000}
        />
      </label>

      <fieldset className="documentPicker">
        <legend>Knowledge documents</legend>
        {indexedDocuments.length === 0 ? (
          <span className="muted">No indexed documents available.</span>
        ) : (
          indexedDocuments.map((document) => (
            <label key={document.id} className="checkItem">
              <input
                type="checkbox"
                checked={selectedDocs.includes(document.id)}
                onChange={() => toggleDocument(document.id)}
              />
              <span>{document.original_filename}</span>
            </label>
          ))
        )}
      </fieldset>

      <button className="primaryButton" type="submit" disabled={isRunning || !prompt.trim()}>
        {isRunning ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
        <span>{isRunning ? "Running Comparison" : "Run Comparison"}</span>
      </button>
    </form>
  );
}

