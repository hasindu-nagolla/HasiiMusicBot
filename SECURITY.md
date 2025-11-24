# 🔒 Security Policy

## 🚨 Reporting a Vulnerability

We take the security of **HasiiMusicBot** seriously. We appreciate your efforts to responsibly disclose any security vulnerabilities you find.

If you discover a security vulnerability within this project, please report it immediately and privately. **Please DO NOT open a public GitHub issue.**

### 📬 How to Report

To report a vulnerability, please contact the project maintainer directly on Telegram:

**Telegram User:** `@Lakzexe`

**In your report, please include:**

1.  **Vulnerability Description:** A clear and detailed explanation of the security issue
2.  **Reproduction Steps:** Detailed steps to reproduce the vulnerability (including necessary configuration, code snippets, or logs)
3.  **Version Information:** The version of the project you are using (commit hash, release tag, or branch name)
4.  **Impact Assessment:** Your assessment of the potential impact and severity
5.  **Suggested Fix:** (Optional) Any recommendations for fixing the vulnerability
6.  **Disclosure Timeline:** Your preferred timeline for public disclosure (if applicable)

### ⏱️ Response Timeline

- **Initial Response:** We will acknowledge your message within **48 hours**
- **Status Updates:** Regular updates on the investigation and fix progress
- **Resolution:** We aim to provide a fix or mitigation within **7-14 days** for critical vulnerabilities
- **Credit:** Security researchers will be credited in the release notes (unless anonymity is requested)

## 📋 Supported Versions

To ensure you have the latest security patches and features, we strongly recommend running the latest stable release of **HasiiMusicBot**.

Security updates will generally be provided for the following versions:

| Version | Supported | Security Updates | Notes |
| :--- | :---: | :---: | :--- |
| **Latest Stable Release (HEAD of `main` branch)** | ✅ | ✅ Yes | Fully supported with active security patches |
| Previous Releases (< 30 days old) | ⚠️ | 🔄 Limited | Critical security fixes only |
| Older Releases (> 30 days) | ❌ | ❌ No | Upgrade required |
| Development/Beta Branches | ⚠️ | ❌ No | Use at your own risk |

**⚠️ Important:** If you are running an older version, please upgrade as soon as possible to receive security fixes and the latest features.

## 🛡️ Security Best Practices for Deployment

As **HasiiMusicBot** is a self-hosted Telegram bot, users are responsible for implementing critical security practices:

### 🔐 Credential Protection

* **Never Expose Secrets:** Never commit your **Telegram Bot Token**, **API ID**, **API Hash**, **MongoDB URI**, **Session Strings**, or any other sensitive credentials to version control
* **Use Environment Variables:** Store all credentials in `.env` files (never commit these to git)
* **Rotate Credentials:** Regularly rotate bot tokens and session strings, especially if you suspect compromise
* **Session String Security:** Pyrogram session strings have the same access as your Telegram account - protect them carefully
* **MongoDB Security:** Use strong passwords and enable MongoDB authentication; restrict network access
* **Cookie Files:** If using YouTube cookies for age-restricted content, ensure they're stored securely and not committed to git

### 🖥️ Infrastructure Security

* **Trusted Environments Only:** Run the bot only on secure, trusted systems with restricted access
* **Firewall Configuration:** Configure firewalls to allow only necessary inbound/outbound connections
* **User Permissions:** Run the bot with minimal required system permissions (avoid root/administrator)
* **Log Security:** Protect log files from unauthorized access as they may contain sensitive information
* **Container Security:** If using Docker, follow container security best practices (non-root user, minimal base image)
* **VPS/Server Hardening:** Keep your hosting environment patched and secure

### 📦 Dependency Management

* **Regular Updates:** Keep all Python packages updated to patch known vulnerabilities
  ```bash
  pip install -U -r requirements.txt
  ```
* **Dependency Auditing:** Periodically check for vulnerable dependencies
  ```bash
  pip install safety
  safety check -r requirements.txt
  ```
* **System Dependencies:** Keep FFmpeg, Deno, and system packages updated
* **Python Version:** Use supported Python versions (3.10+) with active security updates

### 👥 Access Control

* **Owner ID Protection:** Set `OWNER_ID` to your Telegram user ID only; never share owner privileges
* **Sudo User Management:** Carefully manage sudo users - they have elevated bot permissions
* **Blacklist Feature:** Use the blacklist feature to block abusive users or chats
* **Authorization System:** Use the `/auth` command to grant playback permissions selectively
* **Admin Verification:** Ensure the bot verifies admin status before executing privileged commands

### 🔍 Monitoring & Incident Response

* **Regular Log Reviews:** Monitor `log.txt` for suspicious activities or unauthorized access attempts
* **Database Backups:** Regularly backup your MongoDB database
* **Incident Response Plan:** Have a plan for responding to security incidents:
  1. Revoke compromised credentials immediately
  2. Review logs for unauthorized access
  3. Assess data exposure
  4. Notify affected users if necessary
  5. Update credentials and redeploy
* **Rate Limiting:** Be aware of Telegram's rate limits to prevent abuse

### ⚠️ Common Vulnerabilities to Avoid

* **❌ Don't:** Commit `.env` files or session files to GitHub
* **❌ Don't:** Share screenshots containing bot tokens or API credentials
* **❌ Don't:** Use the same bot token across multiple deployments
* **❌ Don't:** Run the bot with root privileges
* **❌ Don't:** Expose MongoDB to the public internet without authentication
* **❌ Don't:** Ignore dependency update warnings
* **❌ Don't:** Share your Pyrogram session strings (they provide full account access)

### 🔗 Additional Resources

* [Telegram Bot Security Best Practices](https://core.telegram.org/bots/security)
* [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
* [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
* [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## 📝 Security Audit History

| Date | Type | Severity | Status | Description |
| :--- | :--- | :---: | :--- | :--- |
| *No security incidents reported* | - | - | - | - |

## 🤝 Responsible Disclosure

We follow responsible disclosure practices. Security researchers who report vulnerabilities responsibly will be:

- Acknowledged publicly (unless they prefer to remain anonymous)
- Credited in release notes and security advisories
- Given reasonable time to verify fixes before public disclosure

## 📜 License & Liability

This software is provided "as is" under the MIT License. While we strive to maintain security, users are responsible for their own deployments and should follow best practices outlined above.

---

**Last Updated:** November 24, 2025  
**Contact:** [@Lakzexe](https://t.me/Lakzexe) on Telegram