import { Database, FileUp, Search, Trash2 } from "lucide-react";
import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import type { DocumentRecord, RetrievedChunk } from "../types";

function fileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function KnowledgeBase() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<RetrievedChunk[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      setDocuments(await api.listDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load documents.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    setError("");
    setMessage("");
    try {
      await api.uploadDocument(file);
      setMessage("Document uploaded.");
      setFile(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    }
  }

  async function indexDocument(id: string) {
    setError("");
    setMessage("Indexing document...");
    try {
      await api.indexDocument(id);
      setMessage("Document indexed.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Indexing failed.");
      setMessage("");
      await load();
    }
  }

  async function deleteDocument(id: string) {
    setError("");
    try {
      await api.deleteDocument(id);
      setMessage("Document deleted.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed.");
    }
  }

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) return;
    setError("");
    try {
      const response = await api.searchDocuments(query);
      setResults(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    }
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <div>
          <p className="eyebrow">Knowledge Base</p>
          <h1>Document Retrieval</h1>
          <p>Upload, index, and test retrieval for PDF, TXT, and DOCX files.</p>
        </div>
      </header>

      {error ? <div className="alert danger">{error}</div> : null}
      {message ? <div className="alert info">{message}</div> : null}

      <section className="twoColumn">
        <form className="toolPanel" onSubmit={upload}>
          <h2>Upload document</h2>
          <label className="fileDrop">
            <FileUp size={22} />
            <span>{file ? file.name : "Choose PDF, TXT, or DOCX"}</span>
            <input
              aria-label="Upload document"
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={chooseFile}
            />
          </label>
          <button className="primaryButton" type="submit" disabled={!file}>
            <FileUp size={18} />
            <span>Upload</span>
          </button>
        </form>

        <form className="toolPanel" onSubmit={search}>
          <h2>Search/retrieve test</h2>
          <label className="field">
            <span>Query</span>
            <input
              aria-label="Search query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search indexed knowledge..."
            />
          </label>
          <button className="primaryButton" type="submit" disabled={!query.trim()}>
            <Search size={18} />
            <span>Search</span>
          </button>
        </form>
      </section>

      <section className="contentSection">
        <div className="sectionTitle">
          <h2>Documents</h2>
          <span className="muted">{documents.length} total</span>
        </div>
        {documents.length === 0 ? (
          <div className="emptyState">
            <Database size={22} />
            <strong>No documents uploaded</strong>
          </div>
        ) : (
          <div className="tableWrap">
            <table className="dataTable">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Chunks</th>
                  <th>Size</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((document) => (
                  <tr key={document.id}>
                    <td>
                      <strong>{document.original_filename}</strong>
                      <small>{document.file_extension}</small>
                    </td>
                    <td>
                      <StatusBadge status={document.status} />
                    </td>
                    <td>{document.chunk_count}</td>
                    <td>{fileSize(document.file_size)}</td>
                    <td>
                      <div className="rowActions">
                        <button
                          className="iconTextButton"
                          type="button"
                          onClick={() => indexDocument(document.id)}
                        >
                          <Database size={16} />
                          <span>Index</span>
                        </button>
                        <button
                          className="iconButton danger"
                          type="button"
                          onClick={() => deleteDocument(document.id)}
                          title="Delete document"
                          aria-label={`Delete ${document.original_filename}`}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                      {document.error_message ? <small>{document.error_message}</small> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {results.length ? (
        <section className="contentSection">
          <h2>Retrieved chunks</h2>
          <div className="retrievalGrid">
            {results.map((result) => (
              <article key={result.chunk_id} className="retrievalItem">
                <strong>Score {result.score}</strong>
                <p>{result.text}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </main>
  );
}

