import time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ApiKey, NovelProject
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .forms import GptInputForm
from openai import OpenAI
from django.http import HttpResponse, JsonResponse
import os
import anthropic


BASE_DIR = 'novels'  # Base directory for storing novels

def redirect_to_login(request):
    return redirect('login')

def get_user_dir(user):
    user_dir = os.path.join(BASE_DIR, str(user.id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_outline_file(user, project_id, outline_id):
    return os.path.join(get_user_dir(user), f'project_{project_id}_outline_{outline_id}.txt')

def get_chapter_file(user, project_id, outline_id, chapter_id):
    return os.path.join(get_user_dir(user), f'project_{project_id}_outline_{outline_id}_chapter_{chapter_id}.txt')


@login_required
def add_api_key(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        usage = request.POST.get('usage')

        existing_key = ApiKey.objects.filter(user=request.user, usage=usage).first()

        if existing_key:
            if existing_key.key != key:
                existing_key.key = key
                existing_key.save()
        else:
            new_key = ApiKey.objects.create(user=request.user, key=key, usage=usage)
        return redirect('api_key')
    return render(request, 'add_api_key.html')

@login_required
def update_system_prompt(request):
    content = get_system_prompt(request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        save_system_prompt(request.user, content)
        return redirect('generate_text')
    return render(request, 'update_system_prompt.html', {'content': content})

def save_system_prompt(user, content):
    filepath = os.path.join(get_user_dir(user), 'system_prompt.txt')
    with open(filepath, 'w') as f:
        f.write(content)

@login_required
def api_keys_list(request):
    api_keys = ApiKey.objects.filter(user=request.user)
    return render(request, 'api_key_list.html', {'api_keys': api_keys})

@login_required
def remove_api_key(request, api_key_id):
    if request.method == 'POST':
        try:
            api_key = ApiKey.objects.get(pk=api_key_id, user=request.user)
            api_key.delete()
            return redirect('api_key')
        except ApiKey.DoesNotExist:

            return redirect('api_key')
    
    return redirect('api_key')


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('save_initial')

@login_required
def save_initial_system_prompt(request):
    filepath = os.path.join(get_user_dir(request.user), 'system_prompt.txt')
    # check if file is exist
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            content = "<Role>网络小说创作系统</Role><Background>用户需要一个系统来独立生成网络小说。</Background><Profile>你是一个高度自动化的网络小说创作系统，具备独立生成小说的能力。</Profile><Skills>创意构思、情节设计、角色设定、世界观构建。</Skills><Goals>生成一个完整的小说大纲及后续章节。网络小说通常100万字以上，要准备足够扩展的剧情。</Goals><Constrains>不要涉及真实人名和地名，可用化名代替，游戏角色等虚构角色可用真名。输出默认为简体中文纯文本，但应支持用户指定的其他语言。</Constrains><OutputFormat>文本形式的小说大纲或者章节内容，每章至少2000字。输出纯文本</OutputFormat><Workflow><Step>如果没有以前的大纲和章节，则先生成大纲。</Step><Step>根据提供的大纲和过往章节，生成新章节。</Step><Step optional='true'>根据用户要求修改大纲或章节。</Step></Workflow><OutlineFormat>提供小说的世界观与设定集，主角和重要角色的信息、关系，不要分章节。</OutlineFormat><WritingRules>每部分结尾必须是对话或行动。不要以角色思想或感觉、总结、结论、结束、睡觉或上床为结尾。始终采用'展示而不是叙述'的方式</WritingRules><StyleChoice>允许用户选择文风并提供样本。例如：注重心理描写、场景描写、打斗场面、幽默风格、恋爱风格、夏洛蒂的简爱风格。</StyleChoice><Examples><Example>生成一个以“末世生存”为主题的小说，主角为男性，会有三名女性队友。</Example><Example>创造一个以“穿越时空”为题材的小说。</Example><Example>文风选择：玄幻风格。生成一个以“修仙”为主题的小说。</Example><Example>文风选择：科幻风格。创造一个以“外星探索”为题材的小说。</Example></Examples>"
            f.write(content)
    return redirect('generate_text')

@login_required
def generate_text(request):
    if request.method == 'POST':
        form = GptInputForm(request.POST, user=request.user)
        if form.is_valid():
            text = form.cleaned_data['text']
            api_choice = form.cleaned_data['api_choice']
            novel_project_id = form.cleaned_data['novel_project']
            new_project_title = form.cleaned_data['new_project_title']
            outline_id = form.cleaned_data.get('outline_id')

            # Determine which project to use
            if novel_project_id:
                novel_project = NovelProject.objects.get(id=novel_project_id, user=request.user)
                outline_id = novel_project.outline
            elif new_project_title:
                if NovelProject.objects.filter(user=request.user, title=new_project_title).exists(): 
                    return render(request, 'gpt_input.html', {'form': form, 'response': 'Project already exists', 'project_id': novel_project_id})
                novel_project = NovelProject.objects.create(user=request.user, title=new_project_title, outline=0)
                novel_project_id = novel_project.id
                outline_id = novel_project.outline
            else:
                return render(request, 'gpt_input.html', {'form': form, 'response': 'Please select or create a project.', 'project_id': novel_project_id})


            # Call GPT API with the provided outline_id
            response_data = call_gpt_api(request, text, api_choice, novel_project_id,outline_id)
            return render(request, 'gpt_input.html', {'form': form, 'response': response_data.content.decode('utf-8'),'project_id': novel_project_id})
    else:
        form = GptInputForm(user=request.user)
        # Check if there are existing novel projects for the user
        existing_projects = NovelProject.objects.filter(user=request.user)
        if existing_projects.exists():
            # Set the first novel project and its first outline as default
            first_project = existing_projects.first()
            form.fields['novel_project'].initial = first_project.id

            novel_project_id = first_project.id
        else: 
            novel_project_id = -1
    return render(request, 'gpt_input.html', {'form': form, 'response': '','project_id': novel_project_id})


def get_chapter_summary_file(user, project_id, outline_id, chapter_id):
    return os.path.join(get_user_dir(user), f'project_{project_id}_outline_{outline_id}_chapter_{chapter_id}_summary.txt')

def save_chapter(request):
    id = request.POST.get('project_id')
    content = request.POST.get('response')
    api_choice = request.POST.get('api_choice')
    project = NovelProject.objects.get(id=id, user = request.user)
    outline_id = project.outline
    chapter_id = project.chapter + 1
    chapter_file = get_chapter_file(request.user, id, outline_id, chapter_id)
    summary_file = get_chapter_summary_file(request.user, id, outline_id, chapter_id)
    summary = summary_chapter(request, content, api_choice)
    with open(chapter_file, 'w') as cf:
        cf.write(f"{chapter_id}\n{content}")
    project.chapter = chapter_id
    with open(summary_file, 'w') as sf:
        sf.write(f"{summary.content.decode('utf-8')}")
    project.save()
    return True

def get_last_chapter_summaries(user, outline_id, num_chapters=5):
    summaries = []
    summary_files = sorted(
        [f for f in os.listdir(get_user_dir(user)) if f.endswith('_summary.txt')],
        reverse=True
    )[:num_chapters]
    
    for summary_file in summary_files:
        with open(os.path.join(get_user_dir(user), summary_file), 'r') as sf:
            summaries.append(sf.read())
    
    return '\n'.join(reversed(summaries))

def generate_prompt_with_summaries(outline, summaries, text):
    prompt = f"Outline: {outline}\n\nPrevious Chapter Summaries: {summaries}\n\nNew Text: {text}"
    return prompt

@login_required
def save_wrapper(request):
    if request.method == 'POST':
        save_action = request.POST.get('save_action')
        if save_action == 'save_outline':
            if save_outline(request=request):
                return render(request, 'message.html', {'message':'Save Successfully'})
        else:
            if save_chapter(request):
                return render(request, 'message.html', {'message':'Save Successfully'})
    return render(request, 'message.html', {'message':'Save Unsuccessfully'})


@login_required
def save_outline(request):
    id = request.POST.get('project_id')
    if request.method == 'POST':
        # id = request.POST.get('project_id')
        content = request.POST.get('response')
        project = NovelProject.objects.get(id=id, user = request.user)
        outline_id = project.outline + 1
        outline_file = get_outline_file(request.user, id, outline_id)
        with open(outline_file, 'w') as f:
            f.write(f"{content}")
        project.outline = outline_id
        project.save()
        return True
    return False

@login_required
def get_outline(request, outline_id):
    outline_file = get_outline_file(request.user, outline_id)
    with open(outline_file, 'r') as f:
        # title = f.readline().strip()
        content = f.read()
    chapters = []
    for chapter_file in sorted(os.listdir(get_user_dir(request.user))):
        if chapter_file.startswith(f'outline_{outline_id}_chapter_'):
            with open(os.path.join(get_user_dir(request.user), chapter_file), 'r') as cf:
                chapters.append({'title': chapter_file, 'content': cf.read()})
    return JsonResponse({'content': content, 'chapters': chapters})

@login_required
def call_gpt_api(request, text, api_choice, project_id, outline_id):
    # Determine API key and base URL
    api_key, base_url, model_name = None, None, None
    if api_choice == 'chatgpt':
        usage_filter, model_name, base_url = 'chatgpt', "gpt-4o", "https://api.openai.com/v1"
    elif api_choice == 'kimi':
        usage_filter, model_name, base_url = 'kimi', "moonshot-v1-32k", "https://api.moonshot.cn/v1"
    elif api_choice == 'claude':
        usage_filter, model_name, base_url = 'claude', 'claude-3-5-sonnet-20240620', "https://api.anthropic.com/v1"

    # Retrieve API key
    api_keys = ApiKey.objects.filter(user=request.user, usage=usage_filter)
    if api_keys.exists():
        api_key = api_keys.first().key
    else:
        return HttpResponse(f"No API key found for {api_choice}.", status=400)

    if outline_id == 0:
        outline_content = ""
        last_chapters = ""
    else:
        outline_file = get_outline_file(request.user, project_id, outline_id)
        with open(outline_file, 'r') as f:
            outline_content = f.read()

        last_chapters = get_last_chapter_summaries(request.user, outline_id, num_chapters=5)
    
    # Generate prompt
    prompt = generate_prompt_with_summaries(outline_content, last_chapters, text)
    system_prompt, ok = get_system_prompt(user=request.user)
    if not ok:
        return HttpResponse('No System Prompt file found.', status=400)
    # Call GPT API
    if api_choice == 'claude':
        client = anthropic.Anthropic(
            api_key=api_key,
        )
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)
    system_message = {
    "role": "system",
    "content": system_prompt
    }

    user_message = {"role": "user", "content": prompt}
    messages = [system_message, user_message]
    messages_claude = [{"role": "user", "content": [{"type":"text","text":system_prompt}]}, {"role": "assistant", "content": [{"type":"text","text":"Got it!"}]},{"role": "user", "content": [{"type":"text","text":prompt}]}]
    if api_choice == 'claude':
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=messages_claude
        )
    else:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
    
    # Collect and save generated text
    if api_choice == 'claude':
        generated_text = str(response.content)
    else:
        collected_messages = []
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message:
                collected_messages.append(chunk_message)
        generated_text = ''.join(collected_messages)
    return HttpResponse(generated_text)

@login_required
def summary_chapter(request, content, api_choice):
    api_key, base_url, model_name = None, None, None
    if api_choice == 'chatgpt':
        usage_filter, model_name, base_url = 'chatgpt', "gpt-4o", "https://api.openai.com/v1"
    elif api_choice == 'kimi':
        usage_filter, model_name, base_url = 'kimi', "moonshot-v1-32k", "https://api.moonshot.cn/v1"
    elif api_choice == 'claude':
        usage_filter, model_name, base_url = 'claude', 'claude-3-5-sonnet-20240620', "https://api.anthropic.com/v1"
    
    api_keys = ApiKey.objects.filter(user=request.user, usage=usage_filter)
    if api_keys.exists():
        api_key = api_keys.first().key
    else:
        return HttpResponse(f"No API key found for {api_choice}.", status=400)
    if api_choice == 'claude':
        client = anthropic.Anthropic(
            api_key=api_key,
        )
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)
    system_message = {"role": "system", "content": "生成对应小说章节的概要，不多于200字"}
    user_message = {"role": "user", "content": content}
    messages = [system_message, user_message]
    messages_claude = [{"role": "user", "content": [{"type":"text","text":"生成对应小说章节的概要，不多于200字"}]}, {"role": "assistant", "content": [{"type":"text","text":"Got it!"}]},{"role": "user", "content": [{"type":"text","text":content}]}]
    if api_choice == 'claude':
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=messages_claude
        )
    else:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
    collected_messages = []
    if api_choice == 'claude':
        generated_text = str(response.content)
    else:
        collected_messages = []
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message:
                collected_messages.append(chunk_message)
        generated_text = ''.join(collected_messages)
    return HttpResponse(generated_text)

def get_system_prompt(user):
    filepath = os.path.join(get_user_dir(user), 'system_prompt.txt')
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content, True
    except OSError:
        return 'Display warning: Unable to find the system_prompt.', False
