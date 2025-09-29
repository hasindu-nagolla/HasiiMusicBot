from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import git
import shutil
import os
from HasiiMusic import app

@app.on_message(filters.command(["downloadrepo"]))
async def download_repo(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "❌ Please provide a valid GitHub repository URL.\n\n"
            "Example: `/downloadrepo https://github.com/userName/repoName`",
            parse_mode=ParseMode.MARKDOWN
        )

    repo_url = message.command[1]
    status_msg = await message.reply_text("⏬ Cloning the repository...")

    zip_path = await clone_and_zip_repo(repo_url)

    if zip_path:
        try:
            await message.reply_document(
                zip_path,
                caption="✅ Repository downloaded and zipped."
            )
        except Exception as e:
            await message.reply_text(
                f"❌ Failed to send file: `{e}`",
                parse_mode=ParseMode.MARKDOWN
            )
        finally:
            os.remove(zip_path)
    else:
        await message.reply_text(
            "❌ Unable to download the specified GitHub repository.",
            parse_mode=ParseMode.MARKDOWN
        )

    await status_msg.delete()

async def clone_and_zip_repo(repo_url: str) -> str | None:
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = repo_name

    try:
        git.Repo.clone_from(repo_url, repo_path)
        zip_file = shutil.make_archive(repo_path, 'zip', repo_path)
        return zip_file
    except git.exc.GitCommandError as e:
        print(f"Git error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    finally:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
