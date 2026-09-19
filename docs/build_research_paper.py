"""Build the multi-agent collaboration conference-style research manuscript."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, FrameBreak, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

for name, suffix in [('Times-Roman', ''), ('Times-Bold', ' Bold'), ('Times-Italic', ' Italic'), ('Times-BoldItalic', ' Bold Italic')]:
    pdfmetrics.registerFont(TTFont(name, f'/System/Library/Fonts/Supplemental/Times New Roman{suffix}.ttf'))
pdfmetrics.registerFontFamily('Times-Roman', normal='Times-Roman', bold='Times-Bold', italic='Times-Italic', boldItalic='Times-BoldItalic')

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'pdf' / 'Multi_Agent_AI_Collaboration_Framework_IEEE.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = A4
LEFT, RIGHT, TOP, BOTTOM, GAP = 42.52, 42.52, 53, 72, 12.7
CW = (W - LEFT - RIGHT - GAP) / 2
body = ParagraphStyle('Body', fontName='Times-Roman', fontSize=10, leading=11.7,
                      alignment=TA_JUSTIFY, firstLineIndent=10, spaceAfter=3, allowWidows=0, allowOrphans=0)
abstract = ParagraphStyle('Abstract', parent=body, fontName='Times-Bold', fontSize=9,
                          leading=10.6, firstLineIndent=0, spaceAfter=7)
heading = ParagraphStyle('Heading', fontName='Times-Roman', fontSize=10, leading=12,
                         alignment=TA_CENTER, spaceBefore=10, spaceAfter=5, keepWithNext=True)
sub = ParagraphStyle('Sub', parent=body, fontName='Times-Italic', firstLineIndent=0,
                     spaceBefore=5, spaceAfter=3, keepWithNext=True)
ref = ParagraphStyle('Ref', parent=body, fontSize=8, leading=9.5,
                     firstLineIndent=-12, leftIndent=12, spaceAfter=5)
cell = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=8, leading=9.5)
story = []

def p(text, style=body):
    story.append(Paragraph(text, style))

def section(title, paragraphs):
    p(title.upper(), heading)
    for text in paragraphs:
        p(text)

def first_page(canvas, doc):
    title = Paragraph('Multi Agent AI Collaboration Framework: A<br/>Comparative Study of Single-Agent and<br/>Multi Agent LLM System',
                      ParagraphStyle('Title', fontName='Times-Roman', fontSize=22,
                                     leading=25, alignment=TA_CENTER))
    _, th = title.wrap(W - LEFT - RIGHT, 100)
    title.drawOn(canvas, LEFT, H - TOP - th)
    authors = Paragraph('Vishal Yadav, Sujal Kushwaha, Saurabh Yadav, Yash Pratap Singh',
                        ParagraphStyle('Authors', fontName='Times-Roman', fontSize=11,
                                       leading=14, alignment=TA_CENTER))
    _, ah = authors.wrap(W-LEFT-RIGHT, 50)
    authors.drawOn(canvas, LEFT, H-TOP-th-20-ah)
    aff = Paragraph('IMS Engineering College<br/>Ghaziabad, India',
                    ParagraphStyle('Affiliation', fontName='Times-Italic', fontSize=10,
                                   leading=12, alignment=TA_CENTER))
    _, fh = aff.wrap(W-LEFT-RIGHT, 50)
    aff.drawOn(canvas, LEFT, H-TOP-th-20-ah-7-fh)

def frames(top):
    return [Frame(x, BOTTOM, CW, H-top-BOTTOM, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, id=f'col{i}')
            for i,x in enumerate((LEFT, LEFT+CW+GAP))]

doc = BaseDocTemplate(str(OUT), pagesize=A4, title='Multi Agent AI Collaboration Framework: A Comparative Study of Single-Agent and Multi Agent LLM System',
                      author='Vishal Yadav; Sujal Kushwaha; Saurabh Yadav; Yash Pratap Singh')
doc.addPageTemplates([PageTemplate(id='First', frames=frames(205), onPage=first_page, autoNextPageTemplate='Later'),
                      PageTemplate(id='Later', frames=frames(TOP))])

p('Abstract&#8212;Large language model applications increasingly distribute work among specialized agents, but additional coordination does not by itself establish better performance. This paper presents a web-based multi-agent AI collaboration framework for comparing a single-agent pipeline with a role-based multi-agent workflow on shared academic and technical prompts. The framework combines local model inference, optional document retrieval, persistent experiment records, and a common evaluation interface. Its multi-agent workflow separates research, planning, writing, review, and verification, while the single-agent baseline generates a response through one principal model call. Evaluation considers reference overlap, response quality, requirement coverage, estimated unsupported content, and measured execution time. The design makes the distinction between heuristic scores and observed measurements explicit. This manuscript describes the architecture, implementation, experimental protocol, and limitations of the framework. Model-quality experiments remain pending; no numerical advantage for either architecture is asserted. The framework provides a practical basis for studying when coordination improves task outcomes and whether any improvement justifies its computational overhead.', abstract)
p('Index Terms&#8212;Large language models, multi-agent systems, comparative evaluation, retrieval-augmented generation, local inference.', abstract)

section('I. Introduction', [
'Large language models are used to explain concepts, synthesize information, and draft software designs. A direct application places these responsibilities in a single model interaction. More elaborate applications distribute them across agents with different instructions and shared intermediate outputs. This creates opportunities for specialization but also introduces additional inference calls, longer execution paths, and new points of failure.',
'A convincing comparison therefore needs more than two plausible-looking answers. The prompt, model configuration, available evidence, and evaluation procedure must be visible. A longer response may appear complete while repeating unsupported statements. A reviewed response may improve organization without improving factual correctness. Execution time also matters when the application is intended for interactive use.',
'The framework addresses this comparison problem through an integrated experimental application. Users submit a prompt, inspect outputs from both architectures, examine the multi-agent stages, and review evaluation results together. The contribution is a practical comparison framework and a transparent measurement protocol. Claims of architectural superiority are reserved for experiments with suitable references, repeated runs, and independently assessed outcomes.'
])
section('II. Related Work', [
'SAMVAD [1] studies judicial deliberation through agents representing legal roles and uses retrieval to ground the simulated process. It illustrates how role assignment and shared evidence can structure a domain-specific interaction. The framework applies role separation to general academic and technical response generation rather than judicial simulation.',
'Mohammadi et al. [2] organize LLM agent evaluation around evaluation objectives and evaluation processes. Their survey motivates examining several aspects of performance and documenting how measurements are produced. The framework follows this concern by exposing quality indicators alongside runtime and identifying scores that depend on heuristic assumptions.',
'AutoGen [3] provides infrastructure for applications built from conversing agents, including customizable interaction patterns. MetaGPT [4] explores organized collaboration through specialized roles and structured procedures. These works motivate explicit coordination in the framework, but their published findings cannot establish the performance of the present implementation. The framework requires its own controlled comparison against its single-agent baseline.'
])
section('III. Problem Statement', [
'For a task prompt and a defined evidence collection, the research problem is to determine how a role-based workflow changes response quality, completeness, unsupported content, and latency relative to direct generation. The comparison must account for the additional computation used by the workflow. It must also distinguish a generation failure from a valid response with low quality.',
'The central questions are whether coordination improves demanding tasks, which stages contribute useful revisions, and how the observed benefits vary with task category. A further question is whether an apparent gain reflects better reasoning or merely a larger total inference budget. These questions guide the experimental design rather than imply an expected winner.'
])
section('IV. Objectives', [
'The project aims to implement both architectures behind a common interface, provide optional retrieval from an uploaded knowledge base, retain intermediate agent outputs, and evaluate completed responses using a consistent procedure. A second objective is to make experiment records inspectable so that users can relate a final answer to its prompt, supporting context, workflow stages, and runtime.',
'The research objective is to establish a repeatable comparison process suitable for academic explanations and complex technical prompts. Achieving this objective requires reporting failure rates and measurement limitations as well as successful outputs. Automated indicators support analysis but do not replace expert judgments of factual correctness.'
])
section('V. Proposed System', [
'The framework accepts a prompt and, where available, a reference answer or selected knowledge documents. It executes a single-agent path and a multi-agent path, stores their outputs, and presents the comparison in a browser. A shared evaluation service reduces inconsistencies that would arise from separately implemented scoring procedures.',
'The system separates inference, retrieval, orchestration, persistence, and presentation. This allows experiments to be reviewed without rerunning the model and permits individual services to be tested independently. Retrieval is optional, which supports both open-ended tasks and tasks grounded in a defined document collection.'
])
section('VI. System Architecture', [
'The presentation layer uses React and TypeScript to provide experiment submission, side-by-side results, history, knowledge-base management, and methodology views. FastAPI exposes the backend operations and coordinates requests. The application layer selects a pipeline, retrieves context where applicable, invokes inference, and passes completed responses to the evaluator.',
'Ollama serves the configured local language model, with Llama 3 8B as the project configuration discussed here. LangGraph represents the multi-agent sequence and carries shared state between stages. The inference service is a dependency of both pipelines: an unavailable server or missing model prevents response generation and must be represented as an operational failure.',
'MySQL is the intended relational store for experiment metadata, prompts, response records, evaluations, and agent runs. SQLAlchemy provides data access and Alembic manages schema migrations. FAISS serves a different purpose: it indexes document vectors for similarity retrieval. Keeping vector retrieval separate from relational persistence supports both evidence lookup and structured experiment history.'
])
section('VII. Single-Agent Pipeline', [
'The single-agent pipeline supplies the prompt and available context to one principal model invocation. The model is responsible for interpreting the task, organizing the answer, and producing the final response within that call. The backend records the outcome and elapsed time before evaluation.',
'This path provides an interpretable baseline with limited orchestration overhead. It may be adequate for concise factual explanations or well-specified tasks. However, it does not expose distinct research, review, or verification stages. The baseline should receive the same external evidence as the multi-agent path when the experiment is intended to isolate coordination effects.'
])
section('VIII. Multi-Agent Pipeline', [
'The multi-agent workflow consists of five roles executed through shared state. The Research Agent extracts relevant findings from the supplied context and identifies information gaps. The Planner Agent turns the task and findings into an organized response plan. The Writer Agent develops the draft from that plan.',
'The Reviewer Agent examines relevance, completeness, clarity, and potentially unsupported statements. The Verifier Agent uses the accumulated material to produce a final response and concise verification findings. Stage outputs make it possible to inspect where information was introduced, revised, or retained.',
'These roles represent separate model interactions and instructions; they need not use distinct model weights. Consequently, agreement between stages is not independent evidence of correctness. Shared model biases can persist across the sequence, and a mistaken early interpretation can influence later stages. The verification label describes a workflow responsibility rather than a guarantee that every claim has been proven.'
])
section('IX. Evaluation Methodology', [
'The framework reports five principal dimensions. The interface term accuracy refers to token-level F1 overlap when a reference answer is available. Precision measures the fraction of response tokens matched to the reference, while recall measures coverage of reference tokens. Their harmonic mean provides an overlap indicator:',
])
p('<i>F</i><sub>1</sub> = 2<i>PR</i> / (<i>P</i> + <i>R</i>)                         (1)', ParagraphStyle('Equation', parent=body, alignment=TA_CENTER, firstLineIndent=0, spaceBefore=4, spaceAfter=6))
p('The zero-overlap case is handled explicitly. Token overlap is not semantic or factual accuracy: correct paraphrases may receive low scores, and incorrect statements may share many reference words. When retrieved context substitutes for a reference, the result is better interpreted as evidence overlap. When neither is present, the application labels the score as estimated.')
p('Response quality is a heuristic indicator based on length adequacy, organization, sentence clarity, and lexical usefulness. Completeness estimates coverage of important prompt terms and requirements. Both can favor surface features and should be checked against task-specific human rubrics.')
p('The hallucination indicator estimates unsupported content from substantive sentences with low evidence overlap. Without evidence, it is labeled estimated hallucination risk. Low overlap alone cannot prove that a sentence is false, and high overlap cannot establish that a claim is supported. The indicator is therefore a screening signal rather than a validated factual-error rate.')
p('Execution time is measured using backend wall-clock duration for each pipeline. Overall scoring combines normalized accuracy, quality, completeness, inverse hallucination, and speed benefits. The default weights are 25%, 25%, 20%, 20%, and 10%, respectively. These configurable weights express a chosen preference, not a universal scientific standard; individual metrics should accompany any aggregate result.')
section('X. Implementation Details', [
'The backend separates request handling from pipeline execution and evaluation logic. The frontend renders stored results and exposes operational status. Experiment history links prompts and outputs to their evaluations, while agent-run records preserve intermediate results for inspection. The knowledge-base component supplies retrieved document context through FAISS.',
'The project includes backend and frontend tests, a migration workflow, and benchmark seed prompts. Such checks establish aspects of software behavior, but they do not measure language-model quality. Local inference also depends on the Ollama installation, model availability, memory capacity, and service configuration. These environmental conditions must be recorded in a completed experimental report.'
])
section('XI. Experimental Design', [
'The proposed evaluation uses academic explanation, technical comparison, system design, and evidence-grounded synthesis tasks. Each prompt is evaluated by both pipelines. Reference answers or task rubrics should be prepared before inspecting generated outputs. A library-management architecture prompt, for example, can be assessed for catalog management, circulation, access control, persistence, and treatment of operational requirements.',
'A completed study should document the exact model version, generation settings, hardware, retrieval configuration, evidence snapshot, and prompt set. Repeated runs are needed to estimate variability. Execution order should be alternated or randomized, and warm-up behavior should be separated from steady-state timing. Failed runs should be counted and described rather than silently omitted.',
'Two comparisons are useful: an application-level comparison with each workflow configured as deployed, and a budget-controlled comparison that constrains total inference resources. The first captures user experience; the second helps separate the effect of coordination from extra computation. Reviewer or verifier ablations can further test whether those stages contribute measurable benefits.',
'Human assessment should conceal the pipeline identity and use a common rubric. At least two independent raters and a documented disagreement procedure would strengthen interpretation. Paired per-prompt differences and uncertainty intervals should accompany aggregate scores. These procedures are proposed for the study and are not reported as completed experiments.'
])
section('XII. Result Representation', [
'At the time of this manuscript, a completed model-quality benchmark is not available. Table I records that status explicitly. Operational testing and interface implementation do not justify filling this table with assumed performance values. A later study should report the number of attempted and successful runs, score distributions, latency, and failure categories for both pipelines.'
])
p('TABLE I<br/>CURRENT STATUS OF COMPARATIVE EVALUATION', ParagraphStyle('Caption', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_CENTER, spaceBefore=5, spaceAfter=5, keepWithNext=True))
rows = [['Measure', 'Single-agent', 'Multi-agent']]
for metric in ['Accuracy / overlap', 'Response quality', 'Completeness', 'Hallucination estimate', 'Execution time', 'Overall score']:
    rows.append([metric, 'Not evaluated', 'Not evaluated'])
t = Table([[Paragraph(escape(c),cell) for c in row] for row in rows], colWidths=[CW*.42,CW*.29,CW*.29])
t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.7,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
story.append(t)
section('XIII. Discussion', [
'The main value of the framework is that it exposes the relationship between orchestration and observable outcomes. Intermediate records help determine whether review changed substantive content or merely presentation. A multi-agent response may cover more requirements at the cost of latency, while a direct response may be preferable for a short, well-defined task. These are hypotheses to test with the framework.',
'Retrieval introduces another factor. Improvements may originate from better evidence rather than role separation. Holding the external context fixed and inspecting retrieved passages helps distinguish these effects. Reporting multiple dimensions also prevents a composite score from hiding a substantial tradeoff between answer quality and response time.'
])
section('XIV. Limitations', [
'The current evaluator uses lexical and structural heuristics that require validation against expert assessments. Sparse or incomplete reference answers can distort overlap scores. Retrieval quality depends on document coverage, segmentation, embeddings, and search settings. Repeated use of the same model may propagate correlated errors through several roles.',
'The seeded prompts do not constitute a representative benchmark. Hardware and model-serving conditions affect latency, and local results may not generalize to larger models or hosted deployments. Without completed comparative experiments, this manuscript establishes no performance improvement or statistical significance.'
])
section('XV. Conclusion', [
'The framework provides a web-based framework for comparing direct language-model generation with a structured research, planning, writing, review, and verification workflow. Its architecture integrates local inference, optional retrieval, persistent records, and transparent evaluation. The framework supports investigation of quality and latency tradeoffs while retaining the context needed to interpret each experiment. A completed empirical study is required before drawing conclusions about which architecture performs better for a given class of tasks.'
])
section('XVI. Future Work', [
'Future work will develop a larger task collection with independently reviewed references, calibrate heuristic scores against human judgments, and evaluate repeated paired runs. Budget-controlled experiments and stage ablations will test whether improvements arise from additional computation or particular agent roles. Broader model comparisons, stronger claim-level evidence checks, and reporting of token usage and resource consumption will extend the framework beyond its present prototype.'
])
story.append(FrameBreak())
p('REFERENCES', heading)
for r in [
'[1] P. Devadiga, O. J. Shetty, and P. Agarwal, "SAMVAD: A Multi-Agent System for Simulating Judicial Deliberation Dynamics in India," arXiv preprint arXiv:2509.03793, 2025. [Online]. Available: https://arxiv.org/abs/2509.03793',
'[2] M. Mohammadi, Y. Li, J. Lo, and W. Yip, "Evaluation and Benchmarking of LLM Agents: A Survey," in Proc. 31st ACM SIGKDD Conf. Knowledge Discovery and Data Mining V.2 (KDD \'25), 2025, pp. 6129-6139, doi: 10.1145/3711896.3736570.',
'[3] Q. Wu, G. Bansal, J. Zhang, et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation," arXiv preprint arXiv:2308.08155, 2023. [Online]. Available: https://arxiv.org/abs/2308.08155',
'[4] S. Hong, M. Zhuge, J. Chen, et al., "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework," in Proc. Int. Conf. Learning Representations (ICLR), 2024. [Online]. Available: https://arxiv.org/abs/2308.00352',
]:
    p(escape(r), ref)

doc.build(story)
print(OUT)
