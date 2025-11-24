import { useState } from 'react'
import { Terminal, Copy, Check, Download, Rocket, Database, Code, Server } from 'lucide-react'

const Installation = () => {
  const [copiedStep, setCopiedStep] = useState(null)

  const copyToClipboard = (text, step) => {
    navigator.clipboard.writeText(text)
    setCopiedStep(step)
    setTimeout(() => setCopiedStep(null), 2000)
  }

  const installSteps = [
    {
      icon: Download,
      title: 'Clone Repository',
      command: 'git clone https://github.com/hasindu-nagolla/HasiiMusicBot\ncd HasiiMusicBot',
      description: 'Download the bot source code from GitHub',
    },
    {
      icon: Code,
      title: 'Install Dependencies',
      command: 'pip install -r requirements.txt',
      description: 'Install all required Python packages',
    },
    {
      icon: Database,
      title: 'Configure Environment',
      command: 'cp sample.env .env\n# Edit .env with your credentials',
      description: 'Set up your API keys and database connection',
    },
    {
      icon: Rocket,
      title: 'Launch Bot',
      command: 'bash start',
      description: 'Start the bot and enjoy music streaming',
    },
  ]

  const requirements = [
    { name: 'Python', version: '3.12+', icon: '🐍' },
    { name: 'MongoDB', version: 'Latest', icon: '🍃' },
    { name: 'FFmpeg', version: 'Latest', icon: '🎬' },
    { name: 'Deno', version: 'Latest', icon: '🦕' },
  ]

  const envVars = [
    { key: 'API_ID', desc: 'Telegram API ID from my.telegram.org' },
    { key: 'API_HASH', desc: 'Telegram API Hash from my.telegram.org' },
    { key: 'BOT_TOKEN', desc: 'Bot token from @BotFather' },
    { key: 'MONGO_DB_URI', desc: 'MongoDB connection string' },
    { key: 'OWNER_ID', desc: 'Your Telegram user ID' },
    { key: 'STRING_SESSION', desc: 'Pyrogram session from @StringFatherBot' },
  ]

  return (
    <section id="installation" className="section-padding bg-spotify-surface">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-spotify-green">Quick Installation</span>
          </h2>
          <p className="text-gray-400 text-lg">
            Get your bot up and running in minutes
          </p>
        </div>

        {/* Requirements */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Server className="w-6 h-6 text-spotify-green" />
            Prerequisites
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {requirements.map((req, index) => (
              <div key={index} className="glass p-6 rounded-xl text-center hover:border-spotify-green transition-colors">
                <div className="text-4xl mb-2">{req.icon}</div>
                <div className="font-semibold text-white">{req.name}</div>
                <div className="text-sm text-gray-400">{req.version}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Installation Steps */}
        <div className="space-y-6 mb-12">
          {installSteps.map((step, index) => {
            const Icon = step.icon
            return (
              <div key={index} className="glass p-6 rounded-xl animate-slide-up hover:border-spotify-green transition-colors" style={{ animationDelay: `${index * 0.1}s` }}>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-xl bg-spotify-green flex items-center justify-center text-xl font-bold text-black">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="w-5 h-5 text-spotify-green" />
                      <h3 className="text-xl font-semibold">{step.title}</h3>
                    </div>
                    <p className="text-gray-400 mb-4">{step.description}</p>
                    <div className="relative">
                      <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-sm border border-spotify-surface-light">
                        <code className="text-spotify-green font-mono">{step.command}</code>
                      </pre>
                      <button
                        onClick={() => copyToClipboard(step.command, index)}
                        className="absolute top-2 right-2 p-2 rounded-lg glass hover:bg-spotify-green hover:text-black transition-colors"
                      >
                        {copiedStep === index ? (
                          <Check className="w-4 h-4 text-spotify-green" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Environment Variables */}
        <div className="glass p-8 rounded-xl">
          <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Terminal className="w-6 h-6 text-spotify-green" />
            Required Environment Variables
          </h3>
          <div className="space-y-4">
            {envVars.map((env, index) => (
              <div key={index} className="flex items-start gap-4 p-4 rounded-lg bg-black/30 hover:bg-black/40 transition-colors border border-transparent hover:border-spotify-green/30">
                <code className="text-spotify-green font-mono font-semibold min-w-[150px]">
                  {env.key}
                </code>
                <p className="text-gray-400">{env.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 p-4 rounded-lg bg-spotify-green/10 border border-spotify-green/30">
            <p className="text-spotify-green-light text-sm">
              💡 <strong>Tip:</strong> Copy <code className="text-spotify-green font-mono">sample.env</code> to{' '}
              <code className="text-spotify-green font-mono">.env</code> and fill in your values. Never commit your{' '}
              <code className="text-spotify-green font-mono">.env</code> file to version control!
            </p>
          </div>
        </div>

        {/* Docker Option */}
        <div className="mt-12 glass p-8 rounded-xl">
          <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Server className="w-6 h-6 text-cyan-400" />
            Docker Deployment (Alternative)
          </h3>
          <p className="text-gray-400 mb-4">
            Prefer containers? Deploy with Docker for isolated and reproducible deployments:
          </p>
          <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-sm">
            <code className="text-green-400 font-mono">
              docker build -t hasii-music-bot .{'\n'}
              docker run -d --env-file .env hasii-music-bot
            </code>
          </pre>
        </div>

        {/* Support CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-400 mb-4">Need help with installation?</p>
          <a
            href="https://t.me/Hasindu_Lakshan"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center gap-2"
          >
            Join Support Group
          </a>
        </div>
      </div>
    </section>
  )
}

export default Installation
