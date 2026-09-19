export function Methodology() {
  return (
    <main className="pageShell">
      <header className="pageHeader">
        <div>
          <p className="eyebrow">About / Methodology</p>
          <h1>ShodhAI</h1>
          <p>
            A comparative framework for evaluating Single-Agent and Multi-Agent Large
            Language Model systems.
          </p>
        </div>
      </header>

      <section className="methodGrid">
        <article className="methodPanel">
          <h2>Purpose</h2>
          <p>
            ShodhAI executes the same academic or technical prompt through two different LLM
            architectures and compares the measured outputs.
          </p>
        </article>

        <article className="methodPanel">
          <h2>Multi-Agent workflow</h2>
          <ol className="plainList">
            <li>Research Agent collects context and gaps.</li>
            <li>Planner Agent creates a structured response plan.</li>
            <li>Writer Agent drafts the answer.</li>
            <li>Reviewer Agent checks completeness and risk.</li>
            <li>Verifier Agent produces the final verified response.</li>
          </ol>
        </article>

        <article className="methodPanel">
          <h2>Evaluation metrics</h2>
          <ul className="plainList">
            <li>Accuracy: reference or evidence overlap when available.</li>
            <li>Response Quality: relevance, clarity, organization, coherence, usefulness.</li>
            <li>Hallucination Rate: estimated unsupported factual-claim percentage.</li>
            <li>Completeness: prompt requirement coverage.</li>
            <li>Execution Time: backend wall-clock duration.</li>
          </ul>
        </article>

        <article className="methodPanel">
          <h2>Research integrity</h2>
          <p>
            ShodhAI labels estimated scores and does not assume that Multi-Agent systems are
            always better. Results depend on prompts, references, retrieved documents, local
            hardware, and model behavior.
          </p>
        </article>
      </section>
    </main>
  );
}

