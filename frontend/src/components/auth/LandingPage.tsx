import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, MessageCircle, Globe, ArrowRight, Terminal } from 'lucide-react';

const LandingPage = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0, filter: 'blur(10px)' },
    visible: {
      y: 0,
      opacity: 1,
      filter: 'blur(0px)',
      transition: {
        type: 'spring',
        stiffness: 70,
        damping: 20,
      },
    },
  };

  const floatingVariant = {
    animate: {
      y: [0, -20, 0],
      scale: [1, 1.05, 1],
      transition: {
        duration: 8,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  <div className="min-h-screen bg-zinc-950 text-zinc-50 relative overflow-hidden font-sans flex flex-col">

    <div className="relative z-10 flex-grow flex flex-col items-center justify-center w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">


      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="text-center max-w-4xl mx-auto flex flex-col items-center"
      >

        <motion.div
          variants={itemVariants}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm font-medium mb-8"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="tracking-wide">Live Chatrooms Active</span>
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-[1.1] text-center"
        >
          <span className="text-zinc-50 block">
            Speak Freely.
          </span>
          <span className="text-zinc-400 block">
            Connect Instantly.
          </span>
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-lg md:text-xl text-zinc-400 mb-12 max-w-2xl mx-auto leading-relaxed text-center"
        >
          The premium social layer for students everywhere. Experience <span className="text-zinc-100 font-medium">real-time pseudonymous chatrooms</span> without the social pressure or identity barriers.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center w-full"
        >
          <Link
            to="/signup"
            className="group relative px-8 py-3 bg-zinc-100 text-zinc-950 rounded-full font-bold text-lg transition-all hover:scale-105 active:scale-95 shadow-md hover:bg-white"
          >
            <div className="flex items-center gap-2">
              Start Chatting <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link
            to="/login"
            className="px-8 py-3 rounded-full font-semibold text-lg text-zinc-400 hover:text-zinc-100 border border-zinc-800 hover:bg-zinc-900 transition-all"
          >
            Sign In
          </Link>
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 60 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 w-full"
      >
        <FeatureCard
          icon={<Shield className="w-6 h-6" />}
          title="Encrypted Identity"
          description="Your identity stays cryptographically hidden using UUIDs. Interact freely without revealing who you are."
          gradient="from-emerald-500/20 to-teal-500/5"
          border="group-hover:border-emerald-500/30"
          iconColor="text-emerald-400"
        />
        <FeatureCard
          icon={<MessageCircle className="w-6 h-6" />}
          title="Live Channels"
          description="Jump into vibrant, topic-based public channels. Share memes, thoughts, and ideas instantly."
          gradient="from-blue-500/20 to-indigo-500/5"
          border="group-hover:border-blue-500/30"
          iconColor="text-blue-400"
        />
        <FeatureCard
          icon={<Globe className="w-6 h-6" />}
          title="Open Community"
          description="Connect with students across different colleges. A unified space for open conversation."
          gradient="from-orange-500/20 to-amber-500/5"
          border="group-hover:border-orange-500/30"
          iconColor="text-orange-400"
        />
      </motion.div>
    </div>

    <footer className="border-t border-zinc-900 bg-zinc-950 w-full relative z-10">
      <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-zinc-800 rounded-lg">
            <Terminal className="w-4 h-4 text-zinc-100 fill-current" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">Ano</span>
        </div>

        <div className="flex items-center gap-6 text-sm text-zinc-500">
          <span>© {new Date().getFullYear()} Ano Platform</span>
          <a href="#" className="hover:text-zinc-300 transition-colors">Privacy</a>
          <a href="#" className="hover:text-zinc-300 transition-colors">Terms</a>
        </div>
      </div>
    </footer>
  </div>

};



const FeatureCard = ({ icon, title, description, iconColor }: any) => (
  <motion.div
    whileHover={{ y: -5 }}
    className="group relative p-8 rounded-3xl border border-zinc-800 bg-zinc-900 transition-all duration-300 overflow-hidden hover:border-zinc-700 hover:bg-zinc-800/80"
  >
    <div className="relative z-10">
      <div className={`mb-6 inline-flex p-3 rounded-2xl bg-zinc-800 ring-1 ring-zinc-700 ${iconColor}`}>
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3 text-zinc-50 tracking-tight">{title}</h3>
      <p className="text-zinc-400 leading-relaxed text-sm">
        {description}
      </p>
    </div>
  </motion.div>
);

export default LandingPage;