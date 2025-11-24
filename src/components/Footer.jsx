import { Github, MessageCircle, Heart, ExternalLink } from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const links = {
    product: [
      { name: 'Features', href: '#features' },
      { name: 'Commands', href: '#commands' },
      { name: 'Installation', href: '#installation' },
      { name: 'Documentation', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot#readme' },
    ],
    community: [
      { name: 'Telegram Channel', href: 'https://t.me/TheInfinityAI' },
      { name: 'Support Group', href: 'https://t.me/Hasindu_Lakshan' },
      { name: 'GitHub Issues', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot/issues' },
      { name: 'Contribute', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot/pulls' },
    ],
    resources: [
      { name: 'GitHub Repo', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot' },
      { name: 'Security Policy', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot/security' },
      { name: 'License (MIT)', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot/blob/main/LICENSE' },
      { name: 'Project Structure', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot/blob/main/PROJECT_STRUCTURE.md' },
    ],
  }

  return (
    <footer className="relative z-10 bg-black border-t border-spotify-surface-light">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 rounded-lg bg-spotify-green">
                <MessageCircle className="w-6 h-6 text-black" />
              </div>
              <span className="text-xl font-bold text-spotify-green">HasiiMusicBot</span>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Advanced Telegram music streaming bot with studio-quality audio and powerful features.
            </p>
            <div className="flex gap-4">
              <a
                href="https://github.com/hasindu-nagolla/HasiiMusicBot"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg glass hover:bg-spotify-surface-light hover:text-spotify-green transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://t.me/TheInfinityAI"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg glass hover:bg-spotify-surface-light hover:text-spotify-green transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              {links.product.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    target={link.href.startsWith('http') ? '_blank' : undefined}
                    rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-1"
                  >
                    {link.name}
                    {link.href.startsWith('http') && <ExternalLink className="w-3 h-3" />}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Community Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Community</h3>
            <ul className="space-y-2">
              {links.community.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-spotify-green transition-colors text-sm flex items-center gap-1"
                  >
                    {link.name}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              {links.resources.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-spotify-green transition-colors text-sm flex items-center gap-1"
                  >
                    {link.name}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-spotify-surface-light">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-sm text-center md:text-left">
              © {currentYear} HasiiMusicBot. All rights reserved. Built with{' '}
              <Heart className="w-4 h-4 inline text-spotify-green" /> by{' '}
              <a
                href="https://github.com/hasindu-nagolla"
                target="_blank"
                rel="noopener noreferrer"
                className="text-spotify-green hover:text-spotify-green-light transition-colors"
              >
                Hasindu Nagolla
              </a>
            </p>
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <a href="#home" className="hover:text-spotify-green transition-colors">
                Back to Top ↑
              </a>
            </div>
          </div>
        </div>

        {/* Tech Stack Badge */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            Powered by Python • Pyrogram • PyTgCalls • MongoDB • React • Tailwind CSS
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
