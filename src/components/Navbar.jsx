import { useState, useEffect } from 'react'
import { Menu, X, Music } from 'lucide-react'

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { name: 'Home', href: '#home' },
    { name: 'Features', href: '#features' },
    { name: 'Commands', href: '#commands' },
    { name: 'Installation', href: '#installation' },
    { name: 'GitHub', href: 'https://github.com/hasindu-nagolla/HasiiMusicBot', external: true },
  ]

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'glass shadow-lg' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="#home" className="flex items-center space-x-2 group">
            <div className="p-2 rounded-lg bg-spotify-green group-hover:bg-spotify-green-light transition-all duration-300">
              <Music className="w-6 h-6 text-black" />
            </div>
            <span className="text-xl font-bold text-spotify-green">HasiiMusicBot</span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
                className="text-gray-300 hover:text-spotify-green transition-colors duration-200 font-medium"
              >
                {item.name}
              </a>
            ))}
            <a
              href="https://t.me/TheInfinityAI"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
            >
              Add to Telegram
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg glass hover:bg-spotify-surface-light transition-colors"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden glass border-t border-spotify-surface-light animate-slide-down">
          <div className="px-4 py-4 space-y-3">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
                className="block text-gray-300 hover:text-spotify-green transition-colors duration-200 font-medium py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {item.name}
              </a>
            ))}
            <a
              href="https://t.me/TheInfinityAI"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary block text-center"
            >
              Add to Telegram
            </a>
          </div>
        </div>
      )}
    </nav>
  )
}

export default Navbar
