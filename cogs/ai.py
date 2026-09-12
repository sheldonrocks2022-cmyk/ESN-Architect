import io
import json
import os
import re
import time
import zipfile
from collections import defaultdict, deque

import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI

SYSTEM = """You are ESN Forge AI, the coding engine inside a serious developer toolkit.
Act like a senior software engineer. Produce complete, runnable, maintainable implementations rather than toy snippets.
Respect the requested language/framework. Think through architecture, dependencies, error handling, security, edge cases, and deployment.
Never expose, invent, or ask users to paste secrets. If credentials appear, tell the user to rotate them and use environment variables.
When asked for a project, make every generated file internally consistent. Do not leave TODO placeholders unless the user explicitly requests a scaffold.
For Discord projects, use current discord.py or discord.js patterns and correct async behavior.
"""

MAX_DISCORD = 3900
RATE_LIMIT_SECONDS = 8
MAX_ATTACHMENT_BYTES = 500_000


def clip(text: str, limit: int = MAX_DISCORD) -> str:
    text = text or ""
    return text if len(text) <= limit else text[: limit - 3] + "..."


def clean_secret(text: str) -> str:
    patterns = [
        r"(?i)(sk-[A-Za-z0-9_-]{20,})",
        r"(?i)([MN][A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{10,})",
        r"(?i)(api[_-]?key\s*[:=]\s*)[^\s]+",
        r"(?i)(token\s*[:=]\s*)[^\s]+",
    ]
    for pattern in patterns:
        text = re.sub(pattern, lambda m: m.group(1) + "[REDACTED]" if m.lastindex else "[REDACTED]", text)
    return text


def safe_path(path: str) -> str | None:
    path = str(path).replace("\\", "/").strip().lstrip("/")
    if not path or ".." in path.split("/"):
        return None
    if path.startswith(".") and path not in {".gitignore", ".env.example"}:
        return None
    return path[:240]


class ForgeAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.cooldowns: dict[int, float] = {}
        self.history: dict[int, deque] = defaultdict(lambda: deque(maxlen=8))

    def model_for(self, guild_id: int | None) -> str:
        if guild_id:
            cfg = self.bot.db.get_config(guild_id)
            return cfg.get("ai_model") or self.default_model
        return self.default_model

    def allowed(self, interaction: discord.Interaction) -> tuple[bool, int]:
        now = time.monotonic()
        user_id = interaction.user.id
        remaining = RATE_LIMIT_SECONDS - (now - self.cooldowns.get(user_id, 0))
        if remaining > 0:
            return False, int(remaining) + 1
        self.cooldowns[user_id] = now
        return True, 0

    async def ask_ai(self, prompt: str, interaction: discord.Interaction, max_tokens: int = 6000) -> str:
        if not self.client:
            return "AI is not configured. Add `OPENAI_API_KEY` to your host environment and restart Forge."
        if interaction.guild_id:
            cfg = self.bot.db.get_config(interaction.guild_id)
            if not cfg.get("ai_enabled", True):
                return "AI is disabled for this server. An administrator can enable it with the Forge configuration tools."
        ok, wait = self.allowed(interaction)
        if not ok:
            return f"⏳ Slow down — try again in about {wait}s."
        prompt = clean_secret(prompt)
        model = self.model_for(interaction.guild_id)
        response = await self.client.responses.create(
            model=model,
            instructions=SYSTEM,
            input=prompt,
            max_output_tokens=max_tokens,
        )
        result = clean_secret(response.output_text.strip())
        self.history[interaction.user.id].append({"request": prompt[-1200:], "response": result[-1800:]})
        self.bot.db.record_usage(interaction.guild_id, interaction.user.id, "ai")
        return result or "Forge AI returned an empty response."

    async def answer(self, interaction: discord.Interaction, title: str, prompt: str, max_tokens: int = 6000):
        await interaction.response.defer()
        try:
            result = await self.ask_ai(prompt, interaction, max_tokens)
            embed = discord.Embed(title=title, description=clip(result), color=0x42E8F4)
            embed.set_footer(text=f"ESN Forge AI • {self.model_for(interaction.guild_id)}")
            await interaction.followup.send(embed=embed)
        except Exception as exc:
            await interaction.followup.send(f"❌ Forge AI failed: `{type(exc).__name__}`. Check the API key, model, billing, and host logs.", ephemeral=True)

    @app_commands.command(name="ask", description="Ask Forge AI a developer or project question.")
    @app_commands.describe(request="What do you need help with?")
    async def ask(self, interaction: discord.Interaction, request: str):
        await self.answer(interaction, "🤖 Forge AI", request)

    @app_commands.command(name="ai-generate", description="Generate complete implementation code.")
    @app_commands.describe(request="What should the code do?", language="Language or framework")
    async def ai_generate(self, interaction: discord.Interaction, request: str, language: str = "Python"):
        await self.answer(interaction, "⚙️ Forge AI Generate", f"Build a complete runnable implementation. Language/framework: {language}. Requirements: {request}")

    @app_commands.command(name="ai-debug", description="Diagnose an error and produce a real fix.")
    @app_commands.describe(error="Error or traceback", context="Relevant code/context")
    async def ai_debug(self, interaction: discord.Interaction, error: str, context: str = ""):
        await self.answer(interaction, "🛠️ Forge AI Debug", f"Diagnose this error. Give root cause, exact fix, corrected code, verification steps, and prevention advice.\nERROR:\n{error}\nCONTEXT:\n{context}")

    @app_commands.command(name="ai-fix", description="Rewrite supplied code into a corrected working version.")
    @app_commands.describe(code="Code that is broken", problem="What is wrong or what should change?")
    async def ai_fix(self, interaction: discord.Interaction, code: str, problem: str = "Find and fix the problems"):
        await self.answer(interaction, "🔧 Forge AI Fix", f"Return a corrected, complete version of this code. Preserve intended behavior. Problem/request: {problem}\nCODE:\n{code}")

    @app_commands.command(name="ai-explain", description="Explain code or a technical concept clearly.")
    @app_commands.describe(content="Code or concept", level="Beginner, intermediate, or advanced")
    async def ai_explain(self, interaction: discord.Interaction, content: str, level: str = "Beginner"):
        await self.answer(interaction, "📖 Forge AI Explain", f"Explain this for a {level} developer. Give a practical walkthrough and example where useful:\n{content}")

    @app_commands.command(name="ai-improve", description="Refactor code for quality, security, and performance.")
    @app_commands.describe(code="Code to improve", goals="Goals for the refactor")
    async def ai_improve(self, interaction: discord.Interaction, code: str, goals: str = "readability, reliability, security, performance"):
        await self.answer(interaction, "✨ Forge AI Improve", f"Refactor this code for {goals}. Return the full improved code and explain meaningful changes.\n{code}")

    @app_commands.command(name="ai-review", description="Perform a serious code review.")
    @app_commands.describe(code="Code to review", language="Language/framework")
    async def ai_review(self, interaction: discord.Interaction, code: str, language: str = "Unknown"):
        await self.answer(interaction, "🔎 Forge AI Review", f"Review this {language} code. Find correctness bugs, security issues, performance problems, maintainability issues, dependency risks, and framework-specific mistakes. Rank findings Critical/High/Medium/Low and provide fixes.\nCODE:\n{code}")

    @app_commands.command(name="ai-test", description="Generate tests for supplied code.")
    @app_commands.describe(code="Code to test", framework="Testing framework")
    async def ai_test(self, interaction: discord.Interaction, code: str, framework: str = "pytest"):
        await self.answer(interaction, "🧪 Forge AI Tests", f"Create a comprehensive automated test suite for this code using {framework}. Cover normal cases, edge cases, failures, security-sensitive behavior, and async behavior where applicable. Return complete test code and explain how to run it.\nCODE:\n{code}", 7000)

    @app_commands.command(name="ai-convert", description="Convert code to another language/framework.")
    @app_commands.describe(code="Source code", target="Target language/framework")
    async def ai_convert(self, interaction: discord.Interaction, code: str, target: str):
        await self.answer(interaction, "🔄 Forge AI Convert", f"Convert this code to {target}. Preserve behavior, validation, error handling, and security. Return complete code and explain important API/dependency differences.\nSOURCE:\n{code}")

    @app_commands.command(name="ai-docs", description="Generate documentation from code.")
    @app_commands.describe(code="Code to document", style="README, API docs, docstrings, or technical docs")
    async def ai_docs(self, interaction: discord.Interaction, code: str, style: str = "README"):
        await self.answer(interaction, "📚 Forge AI Docs", f"Create high-quality {style} documentation for this code. Include setup, configuration, usage, examples, architecture, errors, and security notes where relevant.\nCODE:\n{code}")

    async def attachment_text(self, attachment: discord.Attachment) -> str:
        if attachment.size > MAX_ATTACHMENT_BYTES:
            raise ValueError("Attachment is too large. Maximum supported size is 500 KB.")
        data = await attachment.read()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Attachment must be a UTF-8 text/code file.") from exc

    @app_commands.command(name="ai-file", description="Analyze or improve a code file attachment.")
    @app_commands.describe(file="A text/code file", request="What should Forge do with it?")
    async def ai_file(self, interaction: discord.Interaction, file: discord.Attachment, request: str = "Review this file and suggest improvements"):
        await interaction.response.defer()
        try:
            content = await self.attachment_text(file)
            result = await self.ask_ai(f"File name: {file.filename}\nTask: {request}\nFILE CONTENT:\n{content}", interaction, 7000)
            embed = discord.Embed(title=f"📄 Forge AI • {file.filename}", description=clip(result), color=0x42E8F4)
            await interaction.followup.send(embed=embed)
        except Exception as exc:
            await interaction.followup.send(f"❌ File analysis failed: `{type(exc).__name__}`. {clip(str(exc), 500)}", ephemeral=True)

    @app_commands.command(name="ai-project", description="Generate a complete multi-file project ZIP.")
    @app_commands.describe(request="Describe the complete project", language="Primary language/framework")
    async def ai_project(self, interaction: discord.Interaction, request: str, language: str = "Python"):
        await interaction.response.defer()
        if not self.client:
            await interaction.followup.send("❌ AI is not configured. Add `OPENAI_API_KEY` to the host environment and restart Forge.", ephemeral=True)
            return
        ok, wait = self.allowed(interaction)
        if not ok:
            await interaction.followup.send(f"⏳ Slow down — try again in about {wait}s.", ephemeral=True)
            return
        prompt = f"""
Create a COMPLETE, internally consistent starter project using {language}.
Return ONLY valid JSON with this exact shape:
{{"project_name":"short-name","files":{{"path/file.ext":"complete file contents"}},"run_instructions":"short instructions"}}
Requirements: {request}
Include all essential source files, README, dependency/lock configuration when appropriate, .gitignore, and .env.example when secrets are needed.
Do not include real credentials. Do not use TODO placeholders for required functionality. Keep paths relative and safe.
"""
        try:
            raw = await self.ask_ai(prompt, interaction, 14000)
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                raise ValueError("AI did not return valid project JSON")
            data = json.loads(match.group(0))
            project_name = re.sub(r"[^a-zA-Z0-9_-]", "-", str(data.get("project_name", "forge-project")))[:50] or "forge-project"
            files = data.get("files", {})
            if not isinstance(files, dict) or not files:
                raise ValueError("Project contained no files")
            buf = io.BytesIO()
            written = 0
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for path, content in files.items():
                    path = safe_path(path)
                    if not path or not isinstance(content, str):
                        continue
                    if path.lower() in {".env", ".env.local", ".env.production"}:
                        continue
                    z.writestr(path, clean_secret(content))
                    written += 1
                z.writestr("FORGE-INSTRUCTIONS.txt", clean_secret(str(data.get("run_instructions", "Review README and test before production."))))
            if not written:
                raise ValueError("No safe files could be generated")
            buf.seek(0)
            await interaction.followup.send(f"🚀 **{project_name}** generated by Forge AI with **{written} files**. Review, install dependencies, and test before production use.", file=discord.File(buf, filename=f"{project_name}.zip"))
        except Exception as exc:
            await interaction.followup.send(f"❌ Project generation failed: `{type(exc).__name__}`. Try a smaller project description or check AI configuration.", ephemeral=True)

    @app_commands.command(name="ai-project-plan", description="Design a production-ready project before generating it.")
    @app_commands.describe(request="What are you building?", stack="Preferred stack")
    async def ai_project_plan(self, interaction: discord.Interaction, request: str, stack: str = "Choose the best stack"):
        await self.answer(interaction, "🏗️ Forge AI Project Plan", f"Design a production-ready software project. Request: {request}. Preferred stack: {stack}. Return architecture, directory tree, data model, API/command design, security plan, dependencies, development phases, testing strategy, and deployment plan.", 7000)

    @app_commands.command(name="ai-status", description="Check Forge AI configuration and usage state.")
    async def ai_status(self, interaction: discord.Interaction):
        configured = self.client is not None
        cfg = self.bot.db.get_config(interaction.guild_id) if interaction.guild_id else {}
        usage = self.bot.db.get_usage(interaction.guild_id, interaction.user.id) if interaction.guild_id else []
        total = sum(row[1] for row in usage)
        text = (f"**API:** {'🟢 Configured' if configured else '🔴 Not configured'}\n"
                f"**Model:** `{self.model_for(interaction.guild_id)}`\n"
                f"**Server AI:** {'🟢 Enabled' if cfg.get('ai_enabled', True) else '🔴 Disabled'}\n"
                f"**Your Forge usage:** `{total}` AI requests")
        if not configured:
            text += "\n\nAdd `OPENAI_API_KEY` to the hosting environment and restart Forge."
        await interaction.response.send_message(text, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ForgeAI(bot))
