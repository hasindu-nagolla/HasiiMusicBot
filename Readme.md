# HasiiMusicBot Website

Modern, responsive single-page application built with React + Tailwind CSS to showcase HasiiMusicBot features and functionality.

## 🚀 Tech Stack

- **React 18** - Modern UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Next-generation frontend tooling
- **Framer Motion** - Production-ready animation library
- **Lucide React** - Beautiful icon library
- **React Router** - Client-side routing

## 📦 Project Structure

```
docs/
├── public/              # Static assets
│   └── favicon.svg     # Site favicon
├── src/
│   ├── components/     # React components
│   │   ├── Navbar.jsx
│   │   ├── Hero.jsx
│   │   ├── Features.jsx
│   │   ├── Stats.jsx
│   │   ├── Commands.jsx
│   │   ├── Installation.jsx
│   │   ├── Footer.jsx
│   │   └── ParticlesBackground.jsx
│   ├── App.jsx        # Main app component
│   ├── main.jsx       # Entry point
│   └── index.css      # Global styles
├── index.html         # HTML template
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
├── tailwind.config.js # Tailwind configuration
└── postcss.config.js  # PostCSS configuration
```

## 🛠️ Development

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd docs
npm install
```

### Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` to view the site.

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## 🚢 Deployment

This site is automatically deployed to GitHub Pages using GitHub Actions whenever changes are pushed to the `docs/` directory.

### Manual Deployment

1. Build the project:
   ```bash
   npm run build
   ```

2. The GitHub Actions workflow will automatically deploy to GitHub Pages

3. Access your site at: `https://hasindu-nagolla.github.io/HasiiMusicBot/`

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```javascript
theme: {
  extend: {
    colors: {
      primary: { ... },
      accent: { ... },
    },
  },
}
```

### Content

All content is in the component files under `src/components/`. Edit these files to update:

- Hero section content
- Features list
- Commands reference
- Installation steps
- Footer links

### Animations

Custom animations are defined in `tailwind.config.js` under the `animation` and `keyframes` sections.

## 📄 License

MIT License - See parent directory LICENSE file

## 👨‍💻 Developer

Built by [Hasindu Nagolla](https://github.com/hasindu-nagolla)
