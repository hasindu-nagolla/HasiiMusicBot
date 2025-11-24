import { Music, Github, MessageCircle, ArrowRight } from 'lucide-react'

const Hero = () => {
  return (
    <section id="home" className="section-padding min-h-screen flex items-center justify-center pt-20">
      <div className="max-w-7xl mx-auto text-center">
        {/* Animated Music Icon */}
        <div className="mb-8 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-spotify-green rounded-full blur-3xl opacity-30 animate-pulse-slow"></div>
            <div className="relative p-8 rounded-full bg-spotify-green animate-float">
              <Music className="w-20 h-20 text-black" />
            </div>
          </div>
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
          <span className="text-spotify-green">HasiiMusicBot</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 mb-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          Advanced Telegram Music Streaming Bot
        </p>
        
        <p className="text-lg text-gray-400 mb-12 max-w-3xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
          Experience studio-quality audio with YouTube integration, 50+ live radio stations, 
          and powerful queue management for your Telegram voice chats.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <a
            href="https://t.me/TheInfinityAI"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex items-center gap-2"
          >
            <MessageCircle className="w-5 h-5" />
            Add to Telegram
            <ArrowRight className="w-5 h-5" />
          </a>
          
          <a
            href="https://github.com/hasindu-nagolla/HasiiMusicBot"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary flex items-center gap-2"
          >
            <Github className="w-5 h-5" />
            View on GitHub
          </a>
        </div>

        {/* Tech Stack Badges */}
        <div className="flex flex-wrap gap-3 justify-center animate-fade-in" style={{ animationDelay: '0.4s' }}>
          {['Python 3.12+', 'Pyrogram', 'PyTgCalls', 'MongoDB', 'yt-dlp', 'Docker'].map((tech) => (
            <span
              key={tech}
              className="glass px-4 py-2 rounded-full text-sm font-medium hover:bg-spotify-surface-light hover:border-spotify-green transition-all duration-300"
            >
              {tech}
            </span>
          ))}
        </div>

        {/* Scroll Indicator */}
        <div className="mt-20 animate-bounce">
          <a href="#features" className="inline-block">
            <div className="w-6 h-10 border-2 border-spotify-green/30 rounded-full flex items-start justify-center p-2">
              <div className="w-1 h-2 bg-spotify-green rounded-full animate-pulse"></div>
            </div>
          </a>
        </div>
      </div>
    </section>
  )
}

export default Hero
