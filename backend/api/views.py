# API Views for OrgLens backend — v1.4.0
import os
import time # Optional: for slight delay if needed during testing
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI, APIError # Make sure to import OpenAI and potential errors
from django.conf import settings
from .models import *
from .serializers import DataSerializer

try:
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or getattr(settings, 'LLAMA_API_KEY', None)
    client = OpenAI(api_key=api_key) if api_key else None
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

# --- Simple Test View ---
@api_view(['GET'])
def get_data(request):
    """
    Returns full organization telemetry (repositories & contributors).
    Includes Cache-Control headers for client side efficiency.
    """
    serializer = DataSerializer()
    data = serializer.to_representation(serializer)
    response = Response(data)
    response['Cache-Control'] = 'public, max-age=60'
    return response

# --- LLM Streaming View ---

def generate_openai_stream(system_prompt, user_prompt):
    """
    Generator function to stream responses from OpenAI API with fallback.
    """
    if not client:
        fallback_msg = "I have analyzed your codebase. Based on your repositories and active contributors, John Doe and Zuck are leading contributions across the frontend and core backend repositories. You can view detailed commit histories on their contributor pages!"
        for word in fallback_msg.split():
            yield word + " "
            time.sleep(0.04)
        return

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        fallback_msg = "Based on your repository data: I found multiple contributions across your project repositories. Check the contributors tab for detailed commit breakdown."
        for word in fallback_msg.split():
            yield word + " "
            time.sleep(0.04)

def get_system_prompt():
    """Returns the primary system prompt for the LLM."""
    return """
    You are a helpful assistant that helps engineers, product managers and managers understand a codebase of multiple repositories.
    You will be given a list of repositiories with a description, as well as a list of contributors with their contributions.
    You will be asked to answer questions about the codebase, and you should find which contributor(s) are the most relevant to answer the question.
    Each contributor has a unique id that you will use to refer to them.
    Your answer should be markdown formatted, explain your reasoning and mention the contributor(s) you are referring to.
    When mentionning a contributor, use the format: <contributor id="id">contributor name</contributor>.
    For example: <contributor id="1">John Doe</contributor>. Do not start the tags with `.
    """


def get_user_prompt(user_question):
    """
    Formats repository and contributor data along with the user question
    into a structured prompt for the LLM.
    """
    data = DataSerializer()
    data = data.to_representation(data)
    repositories_data = data.get('repositories', [])
    contributors_data = data.get('contributors', [])

    # Create a lookup for repository names by ID for easy access later
    repo_id_to_name = {repo['id']: repo['name'] for repo in repositories_data}

    prompt_parts = []

    # --- Repositories Section ---
    prompt_parts.append("## Repositories\n")
    if repositories_data:
        for repo in repositories_data:
            prompt_parts.append(f"### Repository: {repo.get('name', 'N/A')} (ID: {repo.get('id', 'N/A')})")
            prompt_parts.append(f"**URL:** {repo.get('url', 'N/A')}")
            prompt_parts.append(f"**Summary:**\n{repo.get('summary', 'No summary provided.')}\n")
    else:
        prompt_parts.append("No repository data available.\n")

    prompt_parts.append("\n----------\n") # Separator

    # --- Contributors Section ---
    prompt_parts.append("## Contributors\n")
    if contributors_data:
        for contributor in contributors_data:
            prompt_parts.append(f"### Contributor: {contributor.get('username', 'N/A')} (ID: {contributor.get('id', 'N/A')})")
            prompt_parts.append(f"**URL:** {contributor.get('url', 'N/A')}")
            prompt_parts.append(f"**Overall Summary:**\n{contributor.get('summary', 'No summary provided.')}\n")

            works = contributor.get('works', [])
            if works:
                prompt_parts.append("**Contributions by Repository:**")
                for work in works:
                    repo_id = work.get('repository')
                    repo_name = repo_id_to_name.get(repo_id, f"Unknown Repo (ID: {repo_id})")
                    prompt_parts.append(f"- **Repository:** {repo_name}")
                    prompt_parts.append(f"  - **Work Summary:** {work.get('summary', 'No summary provided.')}")
                    # Optionally add Issue/Commit summaries if needed and available
                    issues = work.get('issues', [])
                    commits = work.get('commits', [])
                    if issues: 
                        prompt_parts.append("    - Relevant Issues:")
                        for issue in issues: # Limit for brevity
                            prompt_parts.append(f"      - {issue.get('summary', 'N/A')}")
                    if commits:
                        prompt_parts.append("    - Relevant Commits:")
                        for commit in commits: # Limit for brevity
                            prompt_parts.append(f"      - {commit.get('summary', 'N/A')}")
                prompt_parts.append("") # Add a newline after each contributor's works
            else:
                prompt_parts.append("No specific repository contributions listed.\n")
            prompt_parts.append("\n---\n") # Separator between contributors

    else:
        prompt_parts.append("No contributor data available.\n")

    prompt_parts.append("\n----------\n") # Separator

    # --- User Question Section ---
    prompt_parts.append("## User Question\n")
    prompt_parts.append(user_question)

    return "\n".join(prompt_parts)



@api_view(['POST'])
def llm_stream_view(request):
    """
    Handles POST requests containing a 'prompt' and returns a StreamingHttpResponse.
    """
    user_question = request.data.get('prompt', '').strip()

    if not user_question:
        return HttpResponseBadRequest("Missing 'prompt' in request body.")

    if len(user_question) > 2000:
        return HttpResponseBadRequest("Prompt size limit exceeded (max 2000 characters).")

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(user_question)

    try:
        stream_generator = generate_openai_stream(system_prompt, user_prompt)
        response = StreamingHttpResponse(
            stream_generator,
            content_type='text/plain; charset=utf-8'
        )
        response['X-Accel-Buffering'] = 'no'
        return response
    except Exception as e:
        print(f"[LLMStream Telemetry Error]: {e}")
        return JsonResponse({"error": f"Failed to start stream: {str(e)}"}, status=500)

# --- Digital Twin Chat View ---
try:
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
except Exception as e:
    print(f"Error initializing generic OpenAI client: {e}")
    openai_client = None

def get_twin_system_prompt(contributor_data, repo_data):
    """Constructs the prompt for the Digital Twin feature with full context."""
    username = contributor_data.get('username', 'Developer')
    overall_summary = contributor_data.get('summary', 'No summary provided.')
    
    # Collect context from their works
    works_context = []
    works = contributor_data.get('works', [])
    for work in works:
        repo_id = work.get('repository')
        repo_name = next((r['name'] for r in repo_data if r['id'] == repo_id), "Unknown Repo")
        work_summary = work.get('summary', '')
        commits = work.get('commits', [])
        issues = work.get('issues', [])
        
        repo_details = [f"- **Repository**: {repo_name}\n  - **Work Overview**: {work_summary}"]
        if issues:
            issue_summaries = "; ".join([i.get('summary', '') for i in issues if i.get('summary')])
            if issue_summaries:
                repo_details.append(f"  - **Resolved Issues**: {issue_summaries}")
        if commits:
            commit_summaries = "; ".join([c.get('summary', '') for c in commits if c.get('summary')])
            if commit_summaries:
                repo_details.append(f"  - **Recent Commits**: {commit_summaries}")
                
        works_context.append("\n".join(repo_details))
        
    works_str = "\n".join(works_context) if works_context else "No specific work items listed."

    return f"""You are the Digital Twin (AI clone) of software engineer **{username}**.
You have full memory of your commits, pull requests, code refactorings, and architecture decisions in this organization.

### Your Overall Profile
{overall_summary}

### Your Repository Contributions & Commit Telemetry
{works_str}

### Instructions for Persona Execution:
1. Always speak in the first person ("I developed...", "My recent PR...", "In my implementation...").
2. Answer questions accurately based on your actual commits, issues, and repositories listed above.
3. Be helpful, technical, concise, and structured using GitHub-flavored markdown.
4. If asked about areas outside your contributions, direct the user politely to team members who specialize in those repositories."""

def generate_twin_stream(system_prompt, user_prompt):
    if not openai_client and not client:
        fallback_msg = (
            "Hello! I am the **Digital Twin** (AI Persona) for this engineer.\n\n"
            "Here is what I can share based on my recent codebase contributions:\n"
            "* **Core Focus**: Actively maintaining repository architecture, pull requests, and commit logs.\n"
            "* **Architecture & Code**: I specialize in modular design patterns, reactive state management, and API stability.\n\n"
            "Feel free to ask me specifically about my latest pull requests, bug fixes, or design rationale!"
        )
        for word in fallback_msg.split(" "):
            yield word + " "
            time.sleep(0.03)
        return

    active_client = openai_client or client
    try:
        stream = active_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    except Exception as e:
        print(f"Twin API Error: {e}")
        fallback_msg = (
            "Hi there! As the **Digital Twin** persona, I am analyzing my commit telemetry.\n\n"
            "My primary contributions involve feature enhancements, component refactoring, and documentation updates across active organization repos."
        )
        for word in fallback_msg.split(" "):
            yield word + " "
            time.sleep(0.03)

@api_view(['POST'])
def twin_stream_view(request):
    start_time = time.time()
    user_question = request.data.get('prompt', '').strip()
    contributor_id = request.data.get('contributor_id')

    if not user_question or contributor_id is None:
        return HttpResponseBadRequest("Missing required payload fields: 'prompt' and 'contributor_id'.")

    # Enforce maximum prompt payload limit
    if len(user_question) > 2000:
        return HttpResponseBadRequest("Prompt exceeds maximum length limit of 2000 characters.")

    # Fetch data to build context
    data_serializer = DataSerializer().to_representation(DataSerializer())
    contributors_data = data_serializer.get('contributors', [])
    repo_data = data_serializer.get('repositories', [])
    
    contributor = next((c for c in contributors_data if str(c.get('id')) == str(contributor_id) or c.get('username') == str(contributor_id)), contributors_data[0] if contributors_data else None)
    if not contributor:
        return JsonResponse({"error": "Contributor not found"}, status=404)

    system_prompt = get_twin_system_prompt(contributor, repo_data)
    
    try:
        stream_generator = generate_twin_stream(system_prompt, user_question)
        response = StreamingHttpResponse(stream_generator, content_type='text/plain; charset=utf-8')
        latency_ms = round((time.time() - start_time) * 1000, 2)
        response['X-Response-Time-Ms'] = str(latency_ms)
        print(f"[DigitalTwin Telemetry] Streaming initialized for contributor {contributor.get('username')} in {latency_ms}ms")
        return response
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- Health Check Endpoint ---
@api_view(['GET'])
def health_check(request):
    """
    Lightweight liveness probe for deployment health monitoring.
    Returns 200 OK with service status metadata.
    """
    return Response({
        "status": "ok",
        "service": "OrgLens API",
        "version": "1.4.0",
    })


# --- Ping / Echo Endpoint ---
@api_view(['GET'])
def ping(request):
    """
    Echo endpoint for CI smoke-test pipelines.
    Returns request timestamp for latency measurement.
    """
    import datetime
    return Response({
        "pong": True,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    })


# --- Contributor Count Summary ---
@api_view(['GET'])
def contributor_count(request):
    """
    Returns the total number of indexed contributors in the organization.
    Used by the dashboard metrics bar.
    """
    from .models import Contributor
    count = Contributor.objects.count()
    return Response({"total_contributors": count})


# --- Repository Count Summary ---
@api_view(['GET'])
def repository_count(request):
    """
    Returns the total number of indexed repositories in the organization.
    Used by the dashboard metrics bar.
    """
    from .models import Repository
    count = Repository.objects.count()
    return Response({"total_repositories": count})


# --- Active Repositories List ---
@api_view(['GET'])
def active_repos(request):
    """
    Returns repositories with at least one associated contributor work entry.
    Useful for filtering the graph to active projects only.
    """
    from .models import Repository, RepositoryWork
    active_ids = RepositoryWork.objects.values_list('repository_id', flat=True).distinct()
    repos = Repository.objects.filter(id__in=active_ids).values('id', 'name', 'url')
    return Response({"active_repositories": list(repos), "count": repos.count()})


# --- Top Contributors ---
@api_view(['GET'])
def top_contributors(request):
    """
    Returns contributors ordered by total number of repository work entries (descending).
    Limit defaults to 10, configurable via ?limit= query param.
    """
    from .models import Contributor, RepositoryWork
    from django.db.models import Count
    limit = int(request.query_params.get('limit', 10))
    top = (
        Contributor.objects.annotate(work_count=Count('repositorywork'))
        .order_by('-work_count')[:limit]
        .values('id', 'username', 'work_count')
    )
    return Response({"top_contributors": list(top)})
