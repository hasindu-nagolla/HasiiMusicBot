import { useState } from 'react'
import { Play, Pause, SkipForward, Square, Settings, Shield, Terminal } from 'lucide-react'

const Commands = () => {
  const [activeTab, setActiveTab] = useState('user')

  const commandCategories = {
    user: {
      title: 'User Commands',
      icon: Play,
      commands: [
        { cmd: '/play', desc: 'Play a song from YouTube URL or search query' },
        { cmd: '/radio', desc: 'Browse and play from 50+ live radio stations' },
        { cmd: '/queue', desc: 'View current queue and now playing track' },
        { cmd: '/ping', desc: 'Check bot status and system statistics' },
        { cmd: '/help', desc: 'Display help menu with all commands' },
        { cmd: '/lang', desc: 'Change bot language (English/Sinhala)' },
      ],
    },
    admin: {
      title: 'Admin Commands',
      icon: Settings,
      commands: [
        { cmd: '/pause', desc: 'Pause current audio stream' },
        { cmd: '/resume', desc: 'Resume paused audio stream' },
        { cmd: '/skip', desc: 'Skip to next track in queue' },
        { cmd: '/stop', desc: 'Stop playback and clear queue' },
        { cmd: '/seek', desc: 'Jump to specific timestamp in track' },
        { cmd: '/auth', desc: 'Authorize user for playback controls' },
        { cmd: '/channelplay', desc: 'Enable channel play mode' },
        { cmd: '/reload', desc: 'Reload admin cache for group' },
      ],
    },
    sudo: {
      title: 'Sudo Commands',
      icon: Shield,
      commands: [
        { cmd: '/stats', desc: 'View comprehensive bot statistics' },
        { cmd: '/broadcast', desc: 'Send message to all bot users' },
        { cmd: '/addsudo', desc: 'Grant sudo privileges to user' },
        { cmd: '/blacklist', desc: 'Block user or chat from using bot' },
        { cmd: '/restart', desc: 'Restart the bot application' },
        { cmd: '/logs', desc: 'Retrieve bot log files' },
        { cmd: '/eval', desc: 'Execute Python code (owner only)' },
      ],
    },
  }

  return (
    <section id="commands" className="section-padding bg-black/30">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-spotify-green">Command Reference</span>
          </h2>
          <p className="text-gray-400 text-lg">
            Complete list of available commands organized by permission level
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {Object.entries(commandCategories).map(([key, category]) => {
            const Icon = category.icon
            return (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full font-semibold transition-all duration-300 ${
                  activeTab === key
                    ? 'bg-spotify-green text-black shadow-lg shadow-spotify-green/50 scale-105'
                    : 'glass hover:bg-spotify-surface-light hover:border-spotify-green'
                }`}
              >
                <Icon className="w-5 h-5" />
                {category.title}
              </button>
            )
          })}
        </div>

        {/* Commands Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {commandCategories[activeTab].commands.map((command, index) => (
            <div
              key={index}
              className="glass p-6 rounded-xl hover:bg-white/15 transition-all duration-300 animate-scale-in"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-start gap-3">
                <Terminal className="w-5 h-5 text-blue-400 mt-1 flex-shrink-0" />
                <div>
                  <code className="text-lg font-mono text-blue-300 font-semibold">
                    {command.cmd}
                  </code>
                  <p className="text-gray-400 mt-2 text-sm">{command.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Command Usage Note */}
        <div className="mt-12 glass p-6 rounded-xl">
          <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-spotify-green" />
            Usage Notes
          </h3>
          <ul className="space-y-2 text-gray-400">
            <li className="flex items-start gap-2">
              <span className="text-spotify-green mt-1">•</span>
              <span>Admin commands require administrator privileges in the group</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-spotify-green mt-1">•</span>
              <span>Sudo commands are restricted to bot owner and authorized sudo users</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-spotify-green mt-1">•</span>
              <span>Use <code className="text-spotify-green font-mono px-1">/help</code> in Telegram to see command examples and syntax</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  )
}

export default Commands
