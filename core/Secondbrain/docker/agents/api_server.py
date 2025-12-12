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
                'description': 'Multi-agent orchestration system with MoE routing',
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
            },
            {
                'name': 'ba_agent',
                'description': 'Business Analytics agent for project health, utilization, time reports, and quoting',
                'script': 'agent_ba.py'
            }
        ],
        'mcp_servers': [
            {
                'name': 'obsidian',
                'description': 'MCP server for Obsidian integration',
                'script': 'mcp_obsidian_server.py'
            },
            {
                'name': 'sharepoint',
                'description': 'MCP server for SharePoint List operations',
                'script': 'mcp_sharepoint_server.py'
            }
        ],
        'routers': [
            {
                'name': 'moe_router',
                'description': 'Mixture of Experts router for intelligent task delegation',
                'script': 'moe_router.py'
            }
        ]
    })

@app.route('/agents/<agent_name>/run', methods=['POST'])
def run_agent_endpoint(agent_name):
    """Trigger an agent to run"""
    valid_agents = {
        'orchestrator': 'agent_orchestrator.py',
        'notebooklm_analyst': 'agent_notebooklm_analyst.py',
        'obsidian_manager': 'agent_obsidian_manager.py',
        'ba_agent': 'agent_ba.py',
        'moe_router': 'moe_router.py'
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

    return jsonify(jobs[job_id])

import google.generativeai as genai

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Configure safety settings for Gemini (example: block none for all categories)
    # You might want to adjust these based on your application's needs
    gemini_safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
else:
    print("GEMINI_API_KEY not found. Gemini API functionality will be disabled.")

@app.route('/gemini/chat', methods=['POST'])
def gemini_chat():
    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API key not configured'}), 500

    data = request.json or {}
    user_prompt = data.get('prompt')
    chat_history = data.get('history', [])
    context = data.get('context', {}) # Retrieve context from the request

    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # --- Construct System Message from Context ---
        system_message_parts = [
            "You are an AI assistant for an Engineering Command Center dashboard. "
            "Your goal is to assist the user with queries related to projects, tasks, tickets, and time reports. "
            "Leverage the provided 'context' to give accurate and relevant answers. "
            "If the context does not contain the exact answer, state that you cannot answer based on the provided information "
            "and suggest what information would be needed."
        ]

        if context.get('currentUser'):
            system_message_parts.append(f"Current User: {context['currentUser']}")
        if context.get('currentTab'):
            system_message_parts.append(f"Active Tab: {context['currentTab']}")

        if context.get('currentProjectDetails'):
            project = context['currentProjectDetails']
            system_message_parts.append(
                f"\n--- Currently Viewing Project ---"
                f"Title: {project.get('title')}, ID: {project.get('id')}"
                f"Status: {project.get('status')}, Priority: {project.get('priority')}, Progress: {project.get('percentComplete')}%"
                f"Assigned To: {project.get('assignee')}, Due Date: {project.get('dueDate')}"
                f"Description: {project.get('description')}"
                f"Budget Hours: {project.get('budgetHours')}, Hours Spent: {project.get('hoursSpent')}"
            )

        if context.get('currentTicketDetails'):
            ticket = context['currentTicketDetails']
            system_message_parts.append(
                f"\n--- Currently Viewing Ticket ---"
                f"Title: {ticket.get('title')}, ID: {ticket.get('id')}, Number: {ticket.get('ticketNumber')}"
                f"Status: {ticket.get('status')}, Priority: {ticket.get('priority')}"
                f"Assigned To: {ticket.get('assignee')}, Due Date: {ticket.get('dueDate')}"
                f"Description: {ticket.get('description')}"
            )

        if context.get('tasksSummary'):
            system_message_parts.append(f"\n--- Active Tasks Summary ({len(context['tasksSummary'])} tasks) ---")
            for task in context['tasksSummary'][:5]: # Limit to top 5 for brevity
                system_message_parts.append(
                    f"- Task: {task.get('title')} (ID: {task.get('id')}), Status: {task.get('status')}, "
                    f"Priority: {task.get('priority')}, Assignee: {task.get('assignee')}, Due: {task.get('dueDate')}"
                )
            if len(context['tasksSummary']) > 5:
                system_message_parts.append(f"(and {len(context['tasksSummary']) - 5} more tasks)")

        if context.get('projectsSummary'):
            system_message_parts.append(f"\n--- Active Projects Summary ({len(context['projectsSummary'])} projects) ---")
            for project in context['projectsSummary'][:5]: # Limit to top 5 for brevity
                system_message_parts.append(
                    f"- Project: {project.get('title')} (ID: {project.get('id')}), Status: {project.get('status')}, "
                    f"Progress: {project.get('percentComplete')}%, Assignee: {project.get('assignee')}"
                )
            if len(context['projectsSummary']) > 5:
                system_message_parts.append(f"(and {len(context['projectsSummary']) - 5} more projects)")

        if context.get('timeEntriesSummary'):
            system_message_parts.append(f"\n--- Recent Time Entries Summary ({len(context['timeEntriesSummary'])} entries in last 7 days) ---")
            for entry in context['timeEntriesSummary'][:5]: # Limit to top 5 for brevity
                system_message_parts.append(
                    f"- Employee: {entry.get('employee')}, Hours: {entry.get('hours')}h, "
                    f"Project: {entry.get('project')}, Type: {entry.get('type')}, Date: {entry.get('date')}"
                )
            if len(context['timeEntriesSummary']) > 5:
                system_message_parts.append(f"(and {len(context['timeEntriesSummary']) - 5} more time entries)")

        system_message = "\n".join(system_message_parts)

        # Prepend system message to chat history
        formatted_history = []
        if system_message:
            formatted_history.append({"role": "user", "parts": [{"text": system_message}]})
            # This "model" response helps guide the model to acknowledge the context
            formatted_history.append({"role": "model", "parts": [{"text": "Understood. I will use the provided context to assist you. How can I help?"}]})

        # Append the actual chat history sent from the frontend
        for message in chat_history:
            formatted_history.append(message)
        
        # Ensure the conversation history has alternating turns and starts with 'user'
        # The Gemini API expects alternating user/model turns.
        # If the frontend history is malformed, we might need to adjust roles here.
        # However, the frontend is designed to send correct alternating history.
        # So we just append the current user's prompt
        formatted_history.append({"role": "user", "parts": [{"text": user_prompt}]})

        model = genai.GenerativeModel('gemini-pro', safety_settings=gemini_safety_settings)
        # Use the formatted history directly when starting the chat
        chat = model.start_chat(history=formatted_history[:-1]) # history should not include the last user prompt that is sent to send_message
        
        # Send the last user prompt from formatted_history
        response = chat.send_message(formatted_history[-1]["parts"][0]["text"])

        # Extract relevant information from the response
        response_text = ""
        if response.candidates:
            # Join all parts to form the full response text
            response_text = "".join([part.text for part in response.candidates[0].content.parts])
        
        return jsonify({'response': response_text, 'history': chat.history}), 200

    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

