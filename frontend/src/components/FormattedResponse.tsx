import type { ReactNode } from "react";

interface FormattedResponseProps {
  text: string;
  className?: string;
}

type Block =
  | { type: "heading"; text: string; key: string }
  | { type: "paragraph"; text: string; key: string }
  | { type: "unordered"; items: string[]; key: string }
  | { type: "ordered"; items: string[]; key: string }
  | { type: "table"; rows: string[][]; key: string };

function formatInline(text: string): ReactNode[] {
  return text
    .split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g)
    .filter(Boolean)
    .map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("*") && part.endsWith("*")) {
        return <em key={index}>{part.slice(1, -1)}</em>;
      }
      return part;
    });
}

function isTableDivider(line: string) {
  return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line);
}

function parseTableRow(line: string) {
  return line
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function parseBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  let list:
    | { type: "unordered" | "ordered"; items: string[]; key: string }
    | null = null;
  let table: { rows: string[][]; key: string } | null = null;

  function flushList() {
    if (!list) return;
    blocks.push(list);
    list = null;
  }

  function flushTable() {
    if (!table) return;
    if (table.rows.length) {
      blocks.push({ type: "table", rows: table.rows, key: table.key });
    }
    table = null;
  }

  text.split(/\r?\n/).forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      flushTable();
      return;
    }

    if (/^(-{3,}|\*{3,})$/.test(line)) {
      flushList();
      flushTable();
      return;
    }

    if (line.includes("|") && parseTableRow(line).length > 1) {
      flushList();
      if (isTableDivider(line)) return;
      if (!table) {
        table = { rows: [], key: `table-${index}` };
      }
      table.rows.push(parseTableRow(line));
      return;
    }

    flushTable();

    const hashHeading = line.match(/^#{1,6}\s+(.+)$/);
    const romanHeading = line.match(/^([IVXLCDM]+)\.\s+(.+)$/i);
    const heading = hashHeading?.[1] ?? romanHeading?.[2];
    if (heading) {
      flushList();
      blocks.push({ type: "heading", text: heading, key: `h-${index}` });
      return;
    }

    const unordered = line.match(/^[-*]\s+(.+)$/);
    if (unordered) {
      if (!list || list.type !== "unordered") {
        flushList();
        list = { type: "unordered", items: [], key: `ul-${index}` };
      }
      list.items.push(unordered[1]);
      return;
    }

    const ordered = line.match(/^\d+[.)]\s+(.+)$/);
    if (ordered) {
      if (!list || list.type !== "ordered") {
        flushList();
        list = { type: "ordered", items: [], key: `ol-${index}` };
      }
      list.items.push(ordered[1]);
      return;
    }

    flushList();
    blocks.push({ type: "paragraph", text: line, key: `p-${index}` });
  });

  flushList();
  flushTable();
  return blocks;
}

export function FormattedResponse({ text, className = "" }: FormattedResponseProps) {
  const blocks = parseBlocks(text);

  return (
    <div className={`formattedResponse ${className}`.trim()}>
      {blocks.map((block) => {
        if (block.type === "heading") {
          return <h3 key={block.key}>{formatInline(block.text)}</h3>;
        }
        if (block.type === "unordered") {
          return (
            <ul key={block.key}>
              {block.items.map((item, index) => (
                <li key={`${block.key}-${index}`}>{formatInline(item)}</li>
              ))}
            </ul>
          );
        }
        if (block.type === "ordered") {
          return (
            <ol key={block.key}>
              {block.items.map((item, index) => (
                <li key={`${block.key}-${index}`}>{formatInline(item)}</li>
              ))}
            </ol>
          );
        }
        if (block.type === "table") {
          const [header, ...body] = block.rows;
          return (
            <div key={block.key} className="formattedTableWrap">
              <table className="formattedTable">
                {header ? (
                  <thead>
                    <tr>
                      {header.map((cell, index) => (
                        <th key={`${block.key}-h-${index}`}>{formatInline(cell)}</th>
                      ))}
                    </tr>
                  </thead>
                ) : null}
                <tbody>
                  {body.map((row, rowIndex) => (
                    <tr key={`${block.key}-r-${rowIndex}`}>
                      {row.map((cell, cellIndex) => (
                        <td key={`${block.key}-c-${rowIndex}-${cellIndex}`}>
                          {formatInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return <p key={block.key}>{formatInline(block.text)}</p>;
      })}
    </div>
  );
}
