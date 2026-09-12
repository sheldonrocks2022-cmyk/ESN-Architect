import io
import json
import os
import re
import zipfile

import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI


SYSTEM = """You are ESN Forge AI, a practical senior software engineer inside a Discord developer toolkit. Give accurate, production-minded answers. Prefer complete working code over vague advice. Never request or expose passwords, Discord tokens, API keys, or other secrets. If secrets appear in user input, tell the user to rotate them and replace them with environment variables. Respect the requested language/framework. Keep responses Discord-friendly and concise unless the user asks for detail."""


def clip(text: str, limit: int = 3900) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


class ForgeAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def ask_ai(self, prompt: str, max_tokens: int = 5000) -> str:
        if not self.client:
            return "AI is not configured yet. Add `OPENAI_API_KEY` to your hosting environment, then restart Forge."
        response = await self.client.responses.create(
            model=self.model,
            instructions=SYSTEM,
            input=prompt,
            max_output_tokens=max_tokens,
        )
        return response.output_text.strip() or "Forge AI returned an empty response."

    async def answer(self, interaction: discord.Interaction, title: str, prompt: str):
        await interaction.response.defer()
        try:
            result = await self.ask_ai(prompt)
            embed = discord.Embed(title=title, description=clip(result), color=0x42E8F4)
            embed.set_footer(text=f"ESN Forge AI • {self.model}")
            await interaction.followup.send(embed=embed)
        except Exception as exc:
            await interaction.followup.send(f"❌ Forge AI failed: `{type(exc).__name__}`. Check your AI key, model, and host logs.", ephemeral=True)

    @app_commands.command(name="ask", description="Ask Forge AI a general developer or project question.")
    @app_commands.describe(request="What do you need help with?")
    async def ask(self, interaction: discord.Interaction, request: str):
        await self.answer(interaction, "🤖 Forge AI", request)

    @app_commands.command(name="ai-generate", description="Generate real implementation code with Forge AI.")
    @app_commands.describe(request="What should the code do?", language="Programming language/framework")
    async def ai_generate(self, interaction: discord.Interaction, request: str, language: str = "Python"):
        prompt = f"Generate a complete, runnable implementation for this request. Language/framework: {language}. Request: {request}. Include setup/dependencies only when necessary. Put code in fenced blocks and explain how to run it."
        await self.answer(interaction, "⚙️ Forge AI Generate", prompt)

    @app_commands.command(name="ai-debug", description="Use AI to diagnose an error and produce a fix.")
    @app_commands.describe(error="Error/traceback", context="Relevant code or project context")
    async def ai_debug(self, interaction: discord.Interaction, error: str, context: str = ""):
        prompt = f"Diagnose this error. Identify the root cause, exact fix, corrected code when possible, and a prevention step. Error: {error}. Context: {context}"
        await self.answer(interaction, "🛠️ Forge AI Debug", prompt)

    @app_commands.command(name="ai-explain", description="Get a clear AI explanation of code or a concept.")
    @app_commands.describe(content="Code or concept to explain", level="Beginner, intermediate, or advanced")
    async def ai_explain(self, interaction: discord.Interaction, content: str, level: str = "Beginner"):
        await self.answer(interaction, "📖 Forge AI Explain", f"Explain this for a {level} developer. Use a simple walkthrough, key concepts, and a small example when useful: {content}")

    @app_commands.command(name="ai-improve", description="Refactor and improve code with AI.")
    @app_commands.describe(code="Code to improve", goals="Performance, readability, security, etc.")
    async def ai_improve(self, interaction: discord.Interaction, code: str, goals: str = "readability, reliability, security"):
        await self.answer(interaction, "✨ Forge AI Improve", f"Refactor this code for {goals}. Return improved code, explain the important changes, and flag any remaining risks. Code: {code}")

    @app_commands.command(name="ai-review", description="Perform an AI code review.")
    @app_commands.describe(code="Code to review", language="Language/framework")
    async def ai_review(self, interaction: discord.Interaction, code: str, language: str = "Unknown"):
        await self.answer(interaction, "🔎 Forge AI Review", f"Review this {language} code for bugs, security issues, performance problems, maintainability, and Discord-specific issues if applicable. Rank findings by severity and provide fixes. Code: {code}")

    @app_commands.command(name="ai-convert", description="Convert code to another language/framework with AI.")
    @app_commands.describe(code="Source code", target="Target language/framework")
    async def ai_convert(self, interaction: discord.Interaction, code: str, target: str):
        await self.answer(interaction, "🔄 Forge AI Convert", f"Convert this code to {target}. Preserve behavior, error handling, and security. Explain important API/dependency changes. Code: {code}")

    @app_commands.command(name="ai-docs", description="Generate useful documentation from code.")
    @app_commands.describe(code="Code to document", style="README, API docs, docstrings, or technical docs")
    async def ai_docs(self, interaction: discord.Interaction, code: str, style: str = "README"):
        await self.answer(interaction, "📚 Forge AI Docs", f"Create {style} documentation for this code. Include purpose, setup, configuration, usage, inputs/outputs, errors, examples, and security notes where relevant. Code: {code}")

    @app_commands.command(name="ai-project", description="Generate a multi-file project and download it as a ZIP.")
    @app_commands.describe(request="Describe the complete project", language="Primary language/framework")
    async def ai_project(self, interaction: discord.Interaction, request: str, language: str = "Python"):
        await interaction.response.defer()
        if not self.client:
            await interaction.followup.send("❌ AI is not configured. Add `OPENAI_API_KEY` to the host environment and restart Forge.", ephemeral=True)
            return
        prompt = f"Create a complete starter project for this request using {language}. Return ONLY valid JSON in this exact shape: {{\"project_name\":\"short-name\",\"files\":{{\"path/file.ext\":\"complete file contents\"}},\"run_instructions\":\"short instructions\"}}. Include all essential source files, README, dependency file, and .env.example when secrets are needed. Never include real credentials. Request: {request}"
        try:
            raw = await self.ask_ai(prompt, 10000)
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                raise ValueError("AI did not return project JSON")
            data = json.loads(match.group(0))
            project_name = re.sub(r"[^a-zA-Z0-9_-]", "-", str(data.get("project_name", "forge-project")))[:50]
            files = data.get("files", {})
            if not isinstance(files, dict) or not files:
                raise ValueError("Project contained no files")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for path, content in files.items():
                    safe_path = path.replace("\\", "/").lstrip("/")
                    if ".." in safe_path.split("/"):
                        continue
                    if isinstance(content, str):
                        z.writestr(safe_path, content)
                z.writestr("FORGE-INSTRUCTIONS.txt", str(data.get("run_instructions", "Review the generated README before running.")))
            buf.seek(0)
            await interaction.followup.send(f"🚀 **{project_name}** generated by Forge AI. Review and test the project before production use.", file=discord.File(buf, filename=f"{project_name}.zip"))
        except Exception as exc:
            await interaction.followup.send(f"❌ Project generation failed: `{type(exc).__name__}`. Try a smaller project description or check the AI configuration.", ephemeral=True)

    @app_commands.command(name="ai-status", description="Check whether Forge AI is configured.")
    async def ai_status(self, interaction: discord.Interaction):
        configured = self.client is not None
        text = f"Status: {'🟢 Configured' if configured else '🔴 Not configured'}\nModel: `{self.model}`"
        if not configured:
            text += "\nAdd `OPENAI_API_KEY` to the hosting environment and restart Forge."
        await interaction.response.send_message(text, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ForgeAI(bot))
