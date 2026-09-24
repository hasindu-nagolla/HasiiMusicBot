# Contributing to ˹ʜᴀꜱɪɪ ᴍᴜꜱɪᴄ˼

First of all, thank you for your interest in contributing to **HasiiMusicBot**! ❤️

Whether you're reporting bugs, suggesting new features, improving documentation, or submitting code, every contribution helps make this project better for the entire community.

Please take a few minutes to read this guide before contributing.

---

# 📑 Table of Contents

- [🚀 Ways to Contribute](#-ways-to-contribute)
  - [Report a Bug](#report-a-bug)
  - [Request a Feature](#request-a-feature)
  - [Submit a Pull Request](#submit-a-pull-request)
- [🛠 Development Setup](#-development-setup)
- [📝 Coding Standards](#-coding-standards)
- [✅ Pull Request Checklist](#-pull-request-checklist)
- [❤️ Thank You](#️-thank-you)

---

# 🚀 Ways to Contribute

There are many ways you can contribute to the project.

- 🐛 Report bugs
- 💡 Suggest new features
- 📖 Improve documentation
- ⚡ Optimize existing code
- 🔧 Fix bugs
- ✨ Add new functionality

Every contribution, no matter how small, is appreciated.

---

## Report a Bug

Before creating a new issue, please check the existing issues to avoid duplicates.

When reporting a bug, include:

- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected behavior.
- Actual behavior.
- Screenshots or logs (if available).
- Your environment:
  - Operating System
  - Python version
  - Deployment method (Local, Docker, VPS, etc.)

> **⚠️ Security Notice**
>
> Never share sensitive information such as:
>
> - Bot Tokens
> - API IDs
> - API Hashes
> - String Sessions
> - MongoDB URIs
> - Private Chat IDs

---

## Request a Feature

Have an idea that could improve **HasiiMusicBot**?

Open a Feature Request and include:

- A clear description of the feature.
- Why the feature would be useful.
- Possible implementation ideas (optional).
- Example use cases (if applicable).

Please keep feature requests focused and practical.

---

## Submit a Pull Request

Contributions through Pull Requests are always welcome.

### 1. Fork the Repository

Fork the repository to your GitHub account.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/HasiiMusicBot.git

cd HasiiMusicBot
```

### 3. Create a New Branch

For new features:

```bash
git checkout -b feature/your-feature-name
```

For bug fixes:

```bash
git checkout -b fix/issue-name
```

### 4. Make Your Changes

Implement your changes while following the project's coding standards.

### 5. Test Your Changes

Before submitting your Pull Request, verify that:

- The bot starts successfully.
- Existing functionality still works.
- Your new changes work as expected.

### 6. Commit Your Changes

Write clear and meaningful commit messages.

Example:

```bash
git commit -m "Add playlist shuffle command"
```

### 7. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 8. Open a Pull Request

Open a Pull Request against the **main** branch.

Please include:

- A summary of your changes.
- Related issue number (if applicable).
- Screenshots (if your changes affect the user interface).

---

# 🛠 Development Setup

## Requirements

Install the following before contributing:

- Python **3.10+**
- FFmpeg
- Deno

Clone the repository.

```bash
git clone https://github.com/lakzexe/HasiiMusicBot.git

cd HasiiMusicBot
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create your environment configuration.

```bash
cp sample.env .env
```

Update all required environment variables inside the `.env` file.

Start the bot.

```bash
bash start
```

or

```bash
python3 -m HasiiMusic
```

---

# 📝 Coding Standards

To keep the codebase clean and maintainable, please follow these guidelines.

### Python Style

- Follow **PEP 8**.
- Write clean and readable code.
- Keep functions focused on a single responsibility.

### Naming

Use descriptive names for:

- Variables
- Functions
- Classes
- Files

Good example:

```python
current_song = get_current_song()
```

Avoid:

```python
x = get()
```

### Comments

Only add comments when they improve readability.

Example:

```python
# Skip the current stream if playback fails.
```

Avoid comments that simply repeat what the code already says.

### Configuration

Never hardcode:

- Bot Tokens
- API credentials
- String Sessions
- Database URIs
- Chat IDs
- User IDs

Always use environment variables or configuration files.

### Keep It Modular

When adding new features:

- Reuse existing helper functions whenever possible.
- Keep files organized in the appropriate plugin directory.
- Avoid duplicate code.
- Maintain the existing project structure.

---

# ✅ Pull Request Checklist

Before submitting your Pull Request, ensure that:

- [ ] The project builds successfully.
- [ ] The bot starts without errors.
- [ ] Existing functionality is not broken.
- [ ] Your changes have been tested.
- [ ] Code follows the project's coding standards.
- [ ] Documentation has been updated if necessary.
- [ ] No sensitive information has been committed.

---

# ❤️ Thank You

Thank you for taking the time to contribute to **˹ʜᴀꜱɪɪ ᴍᴜꜱɪᴄ˼**.

Every bug report, feature request, documentation improvement, and pull request helps make this project better for everyone.

Your contributions are greatly appreciated, and we're excited to have you as part of the community.

Happy coding! 🚀
