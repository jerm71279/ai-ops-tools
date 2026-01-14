import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Simple web interface for RAG queries - Dual-Store Architecture
Access from browser at http://localhost:5000

Supports:
- Analytical queries (counts, lists) -> SQLite structured store
- Exploratory queries (semantic search) -> ChromaDB vector store
"""
import os
from anthropic import Anthropic
from flask import Flask, render_template_string, request, jsonify
from pathlib import Path
from core.vector_store import VectorStore
from core.obsidian_vault import ObsidianVault
from core.structured_store import StructuredStore
from query_classifier import QueryClassifier, QueryType
from core.config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH
from agentic_rag import AgenticRAG

app = Flask(__name__)

# Load Anthropic API Key for RAG summarization
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = None
if ANTHROPIC_API_KEY:
    try:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}")
        anthropic_client = None
else:
    print("ANTHROPIC_API_KEY not found. LLM summarization/reranking will be disabled in RAG.")

# Initialize stores
vector_store = VectorStore(CHROMA_DB_DIR)
vault = ObsidianVault(OBSIDIAN_VAULT_PATH)
structured_store = StructuredStore(CHROMA_DB_DIR.parent / "structured.db")
query_classifier = QueryClassifier()
agentic_rag = AgenticRAG(structured_store, vector_store) if ANTHROPIC_API_KEY else None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Second Brain RAG</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .stat {
            flex: 1;
            min-width: 150px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .search-box {
            position: relative;
            margin-bottom: 30px;
        }
        input[type="text"] {
            width: 100%;
            padding: 20px;
            font-size: 1.1em;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
            font-weight: 600;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .results {
            margin-top: 30px;
        }
        .llm-summary {
            background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .llm-summary h3 {
            color: #667eea;
            margin-bottom: 12px;
            font-size: 1.1em;
        }
        .llm-summary-content {
            color: #333;
            line-height: 1.7;
            white-space: pre-wrap;
        }
        .result-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .result-card:hover {
            transform: translateX(5px);
        }
        .result-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .result-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .result-tag {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .result-file {
            color: #666;
            font-size: 0.9em;
        }
        .result-score {
            background: #51cf66;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .result-preview {
            color: #555;
            line-height: 1.6;
            margin-top: 10px;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .team-badges {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .team-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .team-badge:hover {
            transform: scale(1.05);
        }
        .team-it { background: #4a9eff; color: white; }
        .team-eng { background: #ff6b6b; color: white; }
        .team-plant { background: #51cf66; color: white; }
        .team-sales { background: #ffd43b; color: #333; }
        .query-type-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 15px;
        }
        .query-type-analytical { background: #4ecdc4; color: white; }
        .query-type-exploratory { background: #667eea; color: white; }
        .query-type-hybrid { background: #ff6b6b; color: white; }
        .structured-answer {
            background: linear-gradient(135deg, #4ecdc422 0%, #44af6922 100%);
            border: 2px solid #4ecdc4;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .structured-answer h3 {
            color: #2d9a8c;
            margin-bottom: 12px;
            font-size: 1.1em;
        }
        .structured-answer-content {
            color: #333;
            line-height: 1.7;
            white-space: pre-wrap;
            font-size: 1.1em;
        }
        .mode-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .mode-toggle label {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 20px;
            background: #f0f0f0;
            transition: all 0.3s;
        }
        .mode-toggle input:checked + label {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
            color: white;
        }
        .mode-toggle input {
            display: none;
        }
        .agent-answer {
            background: linear-gradient(135deg, #ff6b6b22 0%, #ee5a5a22 100%);
            border: 2px solid #ff6b6b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .agent-answer h3 {
            color: #ee5a5a;
            margin-bottom: 12px;
            font-size: 1.1em;
        }
        .agent-answer-content {
            color: #333;
            line-height: 1.7;
        }
        .tools-used {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ffcccc;
            font-size: 0.85em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Second Brain RAG</h1>
        <p class="subtitle">Semantic search across your knowledge base</p>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">486</div>
                <div class="stat-label">Documents Indexed</div>
            </div>
            <div class="stat">
                <div class="stat-value">4</div>
                <div class="stat-label">Teams</div>
            </div>
            <div class="stat">
                <div class="stat-value">186</div>
                <div class="stat-label">Wiki Links</div>
            </div>
        </div>

        <div class="team-badges">
            <div class="team-badge team-it" onclick="search('security policy ITSM')">🔵 IT Services</div>
            <div class="team-badge team-eng" onclick="search('network configuration')">🔴 Engineering</div>
            <div class="team-badge team-plant" onclick="search('site survey installation')">🟢 Plant</div>
            <div class="team-badge team-sales" onclick="search('customer proposal')">🟡 Sales</div>
        </div>

        <div class="search-box">
            <form onsubmit="search(); return false;">
                <input type="text" id="query" placeholder="Ask a question or search for topics..." autofocus>
                <div class="mode-toggle">
                    <input type="checkbox" id="agentMode">
                    <label for="agentMode">Agent Mode (complex queries)</label>
                </div>
                <button type="submit">Search</button>
            </form>
        </div>

        <div class="loading" id="loading">
            <h3>🔍 Searching...</h3>
        </div>

        <div class="results" id="results"></div>
    </div>

    <script>
        function search(presetQuery) {
            const query = presetQuery || document.getElementById('query').value;
            if (!query.trim()) return;

            if (presetQuery) {
                document.getElementById('query').value = query;
            }

            const agentMode = document.getElementById('agentMode').checked;
            const endpoint = agentMode ? '/agent' : '/search';

            document.getElementById('loading').style.display = 'block';
            document.getElementById('loading').innerHTML = agentMode ? '<h3>🤖 Agent thinking...</h3>' : '<h3>🔍 Searching...</h3>';
            document.getElementById('results').innerHTML = '';

            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                console.log('Search response:', data);
                if (!data) {
                    document.getElementById('results').innerHTML = '<div class="no-results">Invalid response from server.</div>';
                    console.error('Invalid response structure:', data);
                    return;
                }
                // Check if this is an agent response
                if (data.agent_answer !== undefined) {
                    displayAgentResults(data);
                } else {
                    displayResults(data.results || [], data.llm_summary, data.query_type, data.structured_data);
                }
            })
            .catch(err => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').innerHTML = '<div class="no-results">Error: ' + err.message + '</div>';
                console.error('Search error:', err);
            });
        }

        function displayResults(results, llmSummary, queryType, structuredData) {
            const container = document.getElementById('results');
            let html = '';

            // Show query type badge
            if (queryType) {
                const typeLabels = {
                    'analytical': 'Database Query',
                    'exploratory': 'Semantic Search',
                    'hybrid': 'Combined Search'
                };
                html += '<span class="query-type-badge query-type-' + queryType + '">' + (typeLabels[queryType] || queryType) + '</span>';
            }

            // For analytical queries, show structured answer prominently
            if (queryType === 'analytical' && structuredData) {
                html += '<div class="structured-answer"><h3>Direct Answer</h3><div class="structured-answer-content">' + structuredData.replace(/\\\\n/g, '<br>') + '</div></div>';
            } else if (llmSummary && !llmSummary.includes('Could not generate')) {
                html += '<div class="llm-summary"><h3>AI Summary</h3><div class="llm-summary-content">' + llmSummary.replace(/\\\\n/g, '<br>') + '</div></div>';
            }

            // Show document results for exploratory/hybrid queries
            if (results && results.length > 0) {
                html += results.map((r, i) => {
                    const metadata = r.metadata || {};
                    const title = metadata.title || 'Untitled';
                    const file = metadata.file_path ? metadata.file_path.split('/').pop() : 'Unknown';
                    let tags = metadata.tags || [];
                    if (typeof tags === 'string') {
                        tags = tags.split(',').map(t => t.trim()).filter(t => t);
                    }
                    const similarity = ((1 - r.distance) * 100).toFixed(1);
                    const preview = (r.content || '').substring(0, 200).replace(/\\\\n/g, ' ') + '...';

                    return '<div class="result-card"><div class="result-title">' + (i + 1) + '. ' + title + '</div><div class="result-meta"><span class="result-score">' + similarity + '% match</span><span class="result-file">📂 ' + file + '</span></div>' + (tags.length > 0 ? '<div class="result-meta">' + tags.slice(0, 5).map(t => '<span class="result-tag">' + t + '</span>').join('') + '</div>' : '') + '<div class="result-preview">' + preview + '</div></div>';
                }).join('');
            } else if (queryType !== 'analytical') {
                html += '<div class="no-results">No document results found. Try different keywords.</div>';
            }

            container.innerHTML = html || '<div class="no-results">No results found.</div>';
        }

        function displayAgentResults(data) {
            const container = document.getElementById('results');
            let html = '<span class="query-type-badge query-type-hybrid">Agent Response</span>';

            if (data.agent_answer) {
                // Convert markdown-style formatting to HTML
                let formattedAnswer = data.agent_answer
                    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/\\n/g, '<br>')
                    .replace(/^## (.+)$/gm, '<h4>$1</h4>')
                    .replace(/^- (.+)$/gm, '<li>$1</li>');

                html += '<div class="agent-answer"><h3>Agent Answer</h3><div class="agent-answer-content">' + formattedAnswer + '</div>';

                // Show tools used
                if (data.tools_used && data.tools_used.length > 0) {
                    html += '<div class="tools-used">Tools used: ' + data.tools_used.map(t => t.tool).join(', ') + '</div>';
                }
                html += '</div>';
            }

            container.innerHTML = html || '<div class="no-results">Agent could not process the query.</div>';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'results': [], 'llm_summary': None, 'query_type': None})

    # Classify the query
    query_type, metadata = query_classifier.classify(query)
    print(f"Query: '{query}' -> Type: {query_type.value}, Intent: {metadata['intent']}, Entities: {metadata['entities']}")

    results = []
    llm_summary = None
    structured_answer = None

    # Handle analytical queries with structured store
    if query_type == QueryType.ANALYTICAL:
        structured_answer = handle_analytical_query(query, metadata)
        llm_summary = structured_answer  # Direct answer for analytical queries

    # Handle exploratory queries with vector store
    elif query_type == QueryType.EXPLORATORY:
        results = vector_store.semantic_search(query, n_results=10)
        if anthropic_client and results:
            llm_summary = generate_llm_summary(query, results)

    # Handle hybrid queries - both stores
    else:
        structured_answer = handle_analytical_query(query, metadata)
        results = vector_store.semantic_search(query, n_results=5)
        if anthropic_client:
            # Combine structured answer with document context
            llm_summary = generate_hybrid_summary(query, structured_answer, results)

    return jsonify({
        'results': results,
        'llm_summary': llm_summary,
        'query_type': query_type.value,
        'structured_data': structured_answer if query_type == QueryType.ANALYTICAL else None
    })


def handle_analytical_query(query: str, metadata: dict) -> str:
    """Handle analytical queries using the structured store"""
    intent = metadata.get('intent')
    entities = metadata.get('entities', [])
    query_lower = query.lower()

    # Customer queries
    if 'customer' in entities or 'client' in entities:
        if intent == 'count' or 'how many' in query_lower:
            # Use folder-based customers for accurate count (these are real customers from SharePoint)
            folder_count = structured_store.query("SELECT COUNT(*) as c FROM customers WHERE source = 'folder'")
            count = folder_count[0]['c'] if folder_count else 0
            customers = structured_store.query("SELECT name FROM customers WHERE source = 'folder' ORDER BY name LIMIT 10")
            customer_names = [c['name'] for c in customers]
            return f"Obera has {count} customers.\\n\\nExamples: {', '.join(customer_names[:5])}{'...' if len(customer_names) > 5 else ''}"
        elif intent == 'list' or 'list' in query_lower:
            customers = structured_store.query("SELECT name FROM customers WHERE source = 'folder' ORDER BY name LIMIT 50")
            if customers:
                names = [c['name'] for c in customers]
                return f"Customer list ({len(names)} shown):\\n" + "\\n".join([f"- {n}" for n in names])
            return "No customers found in the database."
        else:
            stats = structured_store.get_summary_stats()
            return f"Customer summary: {stats['customers']} customers, {stats['projects']} projects, {stats['tickets']} tickets"

    # Project queries
    elif 'project' in entities:
        if intent == 'count' or 'how many' in query_lower:
            count = structured_store.count_projects()
            return f"There are {count} projects in the system."
        elif intent == 'status':
            stats = structured_store.get_project_stats()
            status_breakdown = ", ".join([f"{s['status']}: {s['count']}" for s in stats.get('by_status', [])])
            return f"Project status breakdown: {status_breakdown}" if status_breakdown else "No project status data available."
        else:
            stats = structured_store.get_project_stats()
            return f"Project summary: {stats['total_projects']} total projects"

    # Ticket queries
    elif 'ticket' in entities or 'issue' in entities:
        tickets = structured_store.query("SELECT COUNT(*) as count FROM tickets")
        count = tickets[0]['count'] if tickets else 0
        return f"There are {count} tickets in the system."

    # Employee queries
    elif 'employee' in entities:
        employees = structured_store.query("SELECT COUNT(*) as count FROM employees")
        count = employees[0]['count'] if employees else 0
        return f"There are {count} employees in the system."

    # General stats
    else:
        stats = structured_store.get_summary_stats()
        return f"System overview:\\n- Customers: {stats['customers']}\\n- Projects: {stats['projects']}\\n- Tickets: {stats['tickets']}\\n- Documents: {stats['documents']}\\n- Employees: {stats['employees']}"


def generate_llm_summary(query: str, results: list) -> str:
    """Generate LLM summary for exploratory queries"""
    if not anthropic_client or not results:
        return None

    context_str = "\\n---\\n".join([
        f"Document {i+1} (Source: {r['metadata'].get('file_path', 'unknown')})\\n{r['content']}"
        for i, r in enumerate(results)
    ])

    llm_prompt = f"""You are a helpful assistant. Based on the following documents, summarize the relevant information to answer the query "{query}".
If you cannot find a direct answer, state that you cannot answer based on the provided documents.
Keep the summary concise and directly address the query.

--- Documents ---
{context_str}

--- Query ---
{query}

--- Summary ---
"""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": llm_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error calling Anthropic API for summary: {e}")
        return "Could not generate LLM summary due to an error."


def generate_hybrid_summary(query: str, structured_answer: str, results: list) -> str:
    """Generate summary combining structured data and document context"""
    if not anthropic_client:
        return structured_answer

    doc_context = ""
    if results:
        doc_context = "\\n---\\n".join([
            f"Document: {r['metadata'].get('title', 'Unknown')}\\n{r['content'][:500]}"
            for r in results[:3]
        ])

    llm_prompt = f"""You are a helpful assistant. Combine the structured data answer with relevant document context to provide a complete response.

--- Structured Data Answer ---
{structured_answer}

--- Related Documents ---
{doc_context}

--- Query ---
{query}

--- Combined Summary ---
"""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": llm_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error calling Anthropic API for hybrid summary: {e}")
        return structured_answer

@app.route('/agent', methods=['POST'])
def agent_query():
    """Handle agent mode queries with tool use"""
    query = request.json.get('query', '')
    if not query:
        return jsonify({'agent_answer': None, 'tools_used': [], 'error': 'No query provided'})

    if not agentic_rag:
        return jsonify({'agent_answer': 'Agent mode requires ANTHROPIC_API_KEY to be set.', 'tools_used': []})

    try:
        result = agentic_rag.query(query)
        return jsonify({
            'agent_answer': result.get('answer', ''),
            'tools_used': result.get('tool_calls', []),
            'iterations': result.get('iterations', 0)
        })
    except Exception as e:
        print(f"Agent error: {e}")
        return jsonify({'agent_answer': f'Agent error: {str(e)}', 'tools_used': []})


if __name__ == '__main__':
    print("=" * 80)
    print("🌐 Second Brain RAG Web Interface")
    print("=" * 80)
    print()
    print("✅ Starting web server...")
    print()
    print("📍 Open in your browser:")
    print("   http://localhost:5000")
    print()
    print("💡 Access from other devices on your network:")
    print("   http://YOUR-IP:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()

    app.run(host='0.0.0.0', port=5000, debug=False)
