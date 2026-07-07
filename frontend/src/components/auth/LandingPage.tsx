import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, MessageCircle, Globe, ArrowRight, Terminal } from 'lucide-react';

const LandingPage = () => {
  // Staggered animation configuration
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

  return (
    <div className="min-h-screen pt-12 bg-[#020617] text-white relative overflow-hidden font-sans selection:bg-indigo-500/30 flex flex-col">
      
      {/* --- PREMIUM BACKGROUND LAYER --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Subtle Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.15]" 
          style={{ 
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.1) 1px, transparent 0)', 
            backgroundSize: '40px 40px' 
          }} 
        />
        
        {/* Cinematic Gradient Orbs */}
        <motion.div 
          variants={floatingVariant}
          animate="animate"
          className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-indigo-600/20 rounded-full blur-[120px]" 
        />
        <motion.div 
          variants={floatingVariant}
          animate="animate"
          transition={{ delay: 2 }}
          className="absolute top-[20%] right-[-10%] w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px]" 
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#020617]/50 to-[#020617]" />
      </div>

      {/* --- CONTENT LAYER --- */}
      <div className="relative z-10 flex-grow flex flex-col items-center justify-center w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        
        {/* Hero Section */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center max-w-4xl mx-auto flex flex-col items-center"
        >
          {/* Badge (Updated) */}
          <motion.div 
            variants={itemVariants}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.08] backdrop-blur-md text-indigo-300 text-sm font-medium mb-8 hover:bg-white/[0.06] transition-colors cursor-default"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="tracking-wide">Live Chatrooms Active</span>
          </motion.div>

          {/* H1 Headline (Centered & Updated) */}
          <motion.h1 
            variants={itemVariants}
            className="text-5xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1] text-center"
          >
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 block">
              Speak Freely.
            </span>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-white/90 to-purple-300 block">
               Connect Instantly.
            </span>
          </motion.h1>

          {/* Description (Updated) */}
          <motion.p 
            variants={itemVariants}
            className="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed font-light text-center"
          >
            The premium social layer for students everywhere. Experience <span className="text-white font-medium">real-time pseudonymous chatrooms</span> without the social pressure or identity barriers.
          </motion.p>

          {/* Buttons */}
          <motion.div 
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-5 justify-center items-center w-full"
          >
            <Link 
              to="/signup" 
              className="group relative px-8 py-4 bg-white text-black rounded-full font-bold text-lg transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-10px_rgba(255,255,255,0.4)]"
            >
              <div className="flex items-center gap-2">
                Start Chatting <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
            
            <Link 
              to="/login" 
              className="px-8 py-4 rounded-full font-semibold text-lg text-slate-300 hover:text-white border border-white/10 hover:border-white/20 hover:bg-white/5 transition-all backdrop-blur-sm"
            >
              Sign In
            </Link>
          </motion.div>
        </motion.div>

        {/* --- BENTO GRID FEATURES --- */}
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

      {/* Footer */}
      <footer className="border-t border-white/[0.08] bg-[#020617]/80 backdrop-blur-lg w-full relative z-10">
        <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-indigo-600 rounded-lg">
              <Terminal className="w-4 h-4 text-white fill-current" />
            </div>
            <span className="font-bold text-lg tracking-tight text-white">Ano</span>
          </div>
          
          <div className="flex items-center gap-6 text-sm text-slate-500">
             <span>© {new Date().getFullYear()} Ano Platform</span>
             <a href="#" className="hover:text-slate-300 transition-colors">Privacy</a>
             <a href="#" className="hover:text-slate-300 transition-colors">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

// --- SUB COMPONENTS ---

const FeatureCard = ({ icon, title, description, gradient, border, iconColor }: any) => (
  <motion.div 
    whileHover={{ y: -5 }}
    className={`group relative p-8 rounded-3xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-md transition-all duration-300 overflow-hidden ${border}`}
  >
    {/* Hover Gradient Bloom */}
    <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
    
    <div className="relative z-10">
      <div className={`mb-6 inline-flex p-3 rounded-2xl bg-white/[0.05] ring-1 ring-white/10 ${iconColor}`}>
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3 text-white tracking-tight">{title}</h3>
      <p className="text-slate-400 leading-relaxed text-sm font-light">
        {description}
      </p>
    </div>
  </motion.div>
);

export default LandingPage;