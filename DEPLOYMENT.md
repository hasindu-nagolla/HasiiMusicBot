# GitHub Pages Deployment Guide

## 📋 Prerequisites

Before the GitHub Actions workflow can deploy your site, you need to enable GitHub Pages in your repository settings.

## 🔧 Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/hasindu-nagolla/HasiiMusicBot`
2. Click on **Settings** (top navigation)
3. Scroll down to **Pages** (left sidebar under "Code and automation")
4. Under **Build and deployment**:
   - **Source**: Select **GitHub Actions**
   - Do NOT select "Deploy from a branch"

### 2. Push Your Changes

The workflow is already configured and will trigger automatically when you push changes to the `docs/` folder.

```bash
git add .
git commit -m "Add React website with Spotify theme"
git push origin main
```

### 3. Monitor Deployment

1. Go to the **Actions** tab in your repository
2. You should see the "Deploy React App to GitHub Pages" workflow running
3. Wait for it to complete (usually takes 1-2 minutes)

### 4. Access Your Website

Once deployed, your website will be available at:
```
https://hasindu-nagolla.github.io/HasiiMusicBot/
```

## 🔄 Automatic Deployments

After the initial setup, the website will automatically deploy whenever you:
- Push changes to the `docs/` folder
- Modify the workflow file (`.github/workflows/deploy-docs.yml`)
- Manually trigger the workflow from the Actions tab

## 🐛 Troubleshooting

### Error: "Get Pages site failed"

**Cause**: GitHub Pages is not enabled or not configured for GitHub Actions.

**Solution**: 
1. Go to Settings → Pages
2. Make sure **Source** is set to **GitHub Actions** (not "Deploy from a branch")

### Build Fails

**Check**:
1. Run `npm install` and `npm run build` locally in the `docs/` folder
2. Verify there are no errors
3. Check the Actions logs for specific error messages

### Site Not Updating

1. Clear your browser cache (Ctrl + Shift + R)
2. Wait a few minutes for CDN to update
3. Check if the workflow completed successfully

## 🛠️ Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
cd docs
npm install
npm run build

# The build output will be in docs/dist/
# You can then manually upload this to any static hosting service
```

## 📝 Notes

- First deployment may take 5-10 minutes to become available
- Subsequent deployments are faster (1-2 minutes)
- The workflow only runs when files in `docs/` change
- You can manually trigger deployment from Actions → Deploy React App → Run workflow
