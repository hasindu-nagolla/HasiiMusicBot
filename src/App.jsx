import { HashRouter as Router } from 'react-router-dom'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Features from './components/Features'
import Commands from './components/Commands'
import Installation from './components/Installation'
import Stats from './components/Stats'
import Footer from './components/Footer'
import ParticlesBackground from './components/ParticlesBackground'

function App() {
  return (
    <Router>
      <div className="relative min-h-screen overflow-hidden">
        <ParticlesBackground />
        <Navbar />
        <main className="relative z-10">
          <Hero />
          <Features />
          <Stats />
          <Commands />
          <Installation />
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App
