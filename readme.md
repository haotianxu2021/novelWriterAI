
# novelWriterAI

## Install Guide 安装指南

You need to install Python before installing this application. 你需要在安装此应用程序之前安装Python。

Open your terminal or cmd, open a location where you want to install this application, then type the following command: 打开你的终端或cmd，打开你想安装此应用程序的位置，然后输入以下命令：

```bash
git clone https://github.com/haotianxu2021/novelWriterAI.git

cd novelWriterAI

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

## Usage 使用方法

1. Install the app 安装应用程序
2. Run the server 运行服务器
3. Create an account (It's running locally on your machine and your account info will stay locally. But you have to do this step.) 创建一个账户（它在你的机器上本地运行，你的账户信息将保留在本地。但你必须执行这一步。）
4. Login 登录
5. Add your own api keys for corresponding language models (We support GPT-4o, Kimi and Claude Sonnet 3.5. Note that GPT-4o charge is expensive.) 为相应的语言模型添加你自己的API密钥（我们支持GPT-4o、Kimi和Claude Sonnet 3.5。请注意，GPT-4o的费用很高。）
6. You can begin to generate your novels. 你可以开始生成你的小说。
7. The first request in a new project will generate an outline. You can ask the model to revise the outline. But remember to save the outline after it is done. Only the saved outline will be used in the prompt for the future generation. 新项目的第一个请求将生成一个大纲。你可以让模型修改大纲。但请记住在完成后保存大纲。只有保存的大纲将用于未来的生成提示。
8. If you need to update the outline, you can still ask the model to revise it. Just put the most updated outline in the response and save it. The prompt will use the most updated one. 如果你需要更新大纲，你仍然可以让模型修改它。只需将最新的大纲放入响应中并保存。提示将使用最新的大纲。
9. After the outline is done, you can generate and revise your chapters. Remember to save the chapter so that the next generation has access to it. The prompt will use the summaries of the last five chapters. 大纲完成后，你可以生成和修改你的章节。记住保存章节，以便下一次生成能够访问它。提示将使用最后五个章节的摘要。

## Update 更新日志
0.1.1: Allow revising the system prompt in the "Update System Prompt". 允许在“更新系统提示”中修改系统提示。

0.1.2: Now support Claude. (The max generation length of Claude Sonnet 3.5 is 1024 by API calls, so you decide whether to use it.) 现在支持Claude。（Claude Sonnet 3.5的API最大生成长度是1024，所以你决定是否使用它。）

0.1.3: Fix a bug that you cannot save outline/chapter without generating text first. Now the input prompt will automatically input your last chapter fully (along with the last 5 chapter summaries). 修复了一个无法在未生成文本前保存大纲/章节的错误。现在输入提示将自动完整输入你的最后一章（以及最后五章的摘要）。

## Other Notes 其他说明
Some use suggestions: To make your characters not act as idiots, I suggest you using these Chinese prompts "文风要有逼格，有文学性，有深度". However, it may change your characters to act as idiots in another way. 一些使用建议：为了使你的角色不表现得像白痴，我建议你使用这些中文提示“文风要有逼格，有文学性，有深度”。然而，这可能会让你的角色以另一种方式表现得像白痴。
