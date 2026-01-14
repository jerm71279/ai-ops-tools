import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
AI Agents API Server
Exposes endpoints for agent orchestration and MCP servers
"""
import os
import subprocess
import threading
import asyncio
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Track running jobs and agents
jobs = {}
active_agents = {}

def run_agent(job_id, script_name, args=None):
    """Run an agent script"""
    jobs[job_id]['status'] = 'running'
    jobs[job_id]['started_at'] = datetime.utcnow().isoformat()

    try:
        cmd = ['python', script_name]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour max for long-running agents
        )

        jobs[job_id]['status'] = 'completed' if result.returncode == 0 else 'failed'
        jobs[job_id]['output'] = result.stdout[-10000:]  # Last 10000 chars
        jobs[job_id]['error'] = result.stderr[-2000:] if result.stderr else None
        jobs[job_id]['exit_code'] = result.returncode

    except subprocess.TimeoutExpired:
        jobs[job_id]['status'] = 'timeout'
        jobs[job_id]['error'] = 'Agent exceeded 2 hour timeout'
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

    jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'agents',
        'active_agents': len(active_agents)
    })

@app.route('/agents', methods=['GET'])
def list_agents():
    return jsonify({
        'agents': [
            {
                'name': 'orchestrator',
                'description': 'Multi-agent orchestration system',
                'script': 'agent_orchestrator.py'
            },
            {
                'name': 'notebooklm_analyst',
                'description': 'NotebookLM analysis agent',
                'script': 'agent_notebooklm_analyst.py'
            },
            {
                'name': 'obsidian_manager',
                'description': 'Obsidian vault management agent',
                'script': 'agent_obsidian_manager.py'
            }
        ],
        'mcp_servers': [
            {
                'name': 'obsidian',
                'description': 'MCP server for Obsidian integration',
                'script': 'mcp_obsidian_server.py'
            }
        ]
    })

@app.route('/agents/<agent_name>/run', methods=['POST'])
def run_agent_endpoint(agent_name):
    """Trigger an agent to run"""
    valid_agents = {
        'orchestrator': 'agent_orchestrator.py',
        'notebooklm_analyst': 'agent_notebooklm_analyst.py',
        'obsidian_manager': 'agent_obsidian_manager.py'
    }

    if agent_name not in valid_agents:
        return jsonify({'error': f'Unknown agent: {agent_name}'}), 404

    # Get task from request body
    data = request.json or {}
    task = data.get('task', '')
    args = data.get('args', [])

    if task:
        args = ['--task', task] + args

    job_id = f"{agent_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    jobs[job_id] = {
        'id': job_id,
        'agent': agent_name,
        'task': task,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat()
    }

    thread = threading.Thread(
        target=run_agent,
        args=(job_id, valid_agents[agent_name], args)
    )
    thread.start()

    return jsonify({'job_id': job_id, 'status': 'queued'}), 202

@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """
    Send a task to the orchestrator agent
    Body: {"task": "description of what to do", "context": {...}}
    """
    data = request.json or {}
    task = data.get('task')

    if not task:
        return jsonify({'error': 'Task description required'}), 400

    job_id = f"orchestrator_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    jobs[job_id] = {
        'id': job_id,
        'agent': 'orchestrator',
        'task': task,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat()
    }

    args = ['--task', task]
    if data.get('context'):
        import json
        args.extend(['--context', json.dumps(data['context'])])

    thread = threading.Thread(
        target=run_agent,
        args=(job_id, 'agent_orchestrator.py', args)
    )
    thread.start()

    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Task submitted to orchestrator'
    }), 202

@app.route('/jobs', methods=['GET'])
def list_jobs():
    return jsonify({'jobs': list(jobs.values())})

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
