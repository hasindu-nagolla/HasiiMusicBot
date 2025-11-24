import { useState, useEffect } from 'react'
import { Users, Music as MusicIcon, Radio, TrendingUp } from 'lucide-react'

const Stats = () => {
  const [counters, setCounters] = useState({
    groups: 0,
    songs: 0,
    stations: 0,
    uptime: 0,
  })

  const stats = [
    {
      icon: Users,
      label: 'Active Groups',
      value: '1000+',
      target: 1000,
      key: 'groups',
    },
    {
      icon: MusicIcon,
      label: 'Songs Played',
      value: '50K+',
      target: 50000,
      key: 'songs',
    },
    {
      icon: Radio,
      label: 'Radio Stations',
      value: '50+',
      target: 50,
      key: 'stations',
    },
    {
      icon: TrendingUp,
      label: 'Uptime',
      value: '99.9%',
      target: 99.9,
      key: 'uptime',
    },
  ]

  useEffect(() => {
    const duration = 2000 // 2 seconds
    const steps = 60
    const interval = duration / steps

    stats.forEach(stat => {
      let current = 0
      const increment = stat.target / steps

      const timer = setInterval(() => {
        current += increment
        if (current >= stat.target) {
          current = stat.target
          clearInterval(timer)
        }
        setCounters(prev => ({
          ...prev,
          [stat.key]: Math.floor(current),
        }))
      }, interval)
    })
  }, [])

  return (
    <section className="section-padding bg-spotify-surface">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-spotify-green">Trusted by Thousands</span>
          </h2>
          <p className="text-gray-400 text-lg">
            Join the growing community of music lovers
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={index}
                className="glass p-8 rounded-2xl text-center transform hover:scale-105 transition-all duration-300 animate-scale-in hover:border-spotify-green"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="inline-flex p-4 rounded-2xl bg-spotify-green mb-4">
                  <Icon className="w-8 h-8 text-black" />
                </div>
                <div className="text-4xl font-bold mb-2 text-spotify-green">
                  {stat.value}
                </div>
                <div className="text-gray-400 font-medium">{stat.label}</div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default Stats
