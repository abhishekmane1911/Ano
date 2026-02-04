import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, User, Heart, Zap } from 'lucide-react';
import { GlassCard, GlassInput, RadioCard } from '../ui/Glass';
import InterestSelector from './InterestSelector';
import AnonymousAvatar from './AnonymousAvatar';
import { profileAPI } from '../../api/profile';
import { useProfileStore } from '../../stores/profileStore';


const ProfileCreation = () => {
  const navigate = useNavigate();
  const { setProfile, setLoading, setError } = useProfileStore();
  const [currentStep, setCurrentStep] = useState(1);
  const [direction, setDirection] = useState(0);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState<{
    age: number;
    interests: string[];
    hobbies: string[];
    relationship_intent: 'friendship' | 'dating' | 'casual' | '';
    personality_tags: string[];
    bio: string;
  }>({
    age: 18,
    interests: [],
    hobbies: [],
    relationship_intent: '',
    personality_tags: [],
    bio: ''
  });

  const totalSteps = 4;

  const variants = {
    enter: (direction: number) => ({ x: direction > 0 ? 50 : -50, opacity: 0, filter: "blur(10px)" }),
    center: { zIndex: 1, x: 0, opacity: 1, filter: "blur(0px)" },
    exit: (direction: number) => ({ zIndex: 0, x: direction < 0 ? 50 : -50, opacity: 0, filter: "blur(10px)" })
  };

  const handleNext = async () => {
    if (currentStep < totalSteps) {
      setDirection(1);
      setCurrentStep(prev => prev + 1);
    } else {
      // Handle Final Submit
      setIsSubmitting(true);
      setLoading(true);
      try {
        // Validate relationship_intent is set
        if (!formData.relationship_intent) {
          setError('Please select a relationship intent');
          setIsSubmitting(false);
          setLoading(false);
          return;
        }
        
        // Create profile with properly typed data
        const profileData = {
          age: formData.age,
          interests: formData.interests,
          hobbies: formData.hobbies,
          relationship_intent: formData.relationship_intent as 'friendship' | 'dating' | 'casual',
          personality_tags: formData.personality_tags,
          bio: formData.bio
        };
        
        const profile = await profileAPI.createProfile(profileData);
        if (avatarFile) await profileAPI.uploadAvatar(avatarFile);
        setProfile(profile);
        navigate('/');
      } catch (err: any) {
        setError(err.message || 'Failed to create profile');
      } finally {
        setIsSubmitting(false);
        setLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setDirection(-1);
      setCurrentStep(prev => prev - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500 mb-2">The Basics</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">Let's start with who you are.</p>
            <GlassInput 
              label="Age" 
              type="number" 
              value={formData.age}
              onChange={(e: any) => setFormData({...formData, age: parseInt(e.target.value) || 18})}
              icon={User}
              min="18"
              max="100"
            />
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1">Looking for</label>
              <div className="flex gap-4 flex-wrap">
                <RadioCard 
                  name="intent"
                  value="friendship" 
                  selected={formData.relationship_intent}
                  onChange={(e: any) => setFormData({...formData, relationship_intent: e.target.value})}
                  label="Friends"
                  icon={<User size={20} />}
                />
                <RadioCard 
                  name="intent"
                  value="dating" 
                  selected={formData.relationship_intent}
                  onChange={(e: any) => setFormData({...formData, relationship_intent: e.target.value})}
                  label="Dating"
                  icon={<Heart size={20} />}
                />
                <RadioCard 
                  name="intent"
                  value="casual" 
                  selected={formData.relationship_intent}
                  onChange={(e: any) => setFormData({...formData, relationship_intent: e.target.value})}
                  label="Casual"
                  icon={<Zap size={20} />}
                />
              </div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-2">
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500 mb-2">Passions</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">What makes you tick?</p>
            <InterestSelector 
              label="Interests"
              selectedItems={formData.interests}
              onChange={(items: string[]) => setFormData({...formData, interests: items})}
              suggestions={['Music', 'Tech', 'Art', 'Travel']}
              placeholder="Add interests..."
            />
             <InterestSelector 
              label="Hobbies"
              selectedItems={formData.hobbies}
              onChange={(items: string[]) => setFormData({...formData, hobbies: items})}
              suggestions={['Gaming', 'Hiking', 'Cooking', 'Reading']}
              placeholder="Add hobbies..."
            />
          </div>
        );
      case 3:
         return (
          <div className="space-y-2">
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500 mb-2">Vibe Check</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">Describe your personality.</p>
            <InterestSelector 
              label="Personality Tags"
              selectedItems={formData.personality_tags}
              onChange={(items: string[]) => setFormData({...formData, personality_tags: items})}
              suggestions={['Introvert', 'Extrovert', 'Funny', 'Serious']}
              placeholder="I am..."
            />
          </div>
        );
      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500 mb-2">Final Touches</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">Show them who you are.</p>
            <div className="flex justify-center mb-8">
              <AnonymousAvatar 
                size="large"
                onImageSelect={(file: File) => setAvatarFile(file)} 
              />
            </div>
            <div className="group relative z-0 w-full mb-6">
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                className="block py-3 px-4 w-full text-base text-gray-900 dark:text-white bg-white/5 dark:bg-black/20 border-2 border-white/10 dark:border-white/5 rounded-xl appearance-none focus:outline-none focus:ring-0 focus:border-indigo-500/50 peer transition-all resize-none"
                placeholder=" "
                rows={4}
                maxLength={500}
              />
              <label className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-transparent px-2 peer-placeholder-shown:px-4 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-3 peer-focus:scale-75 peer-focus:-translate-y-4 left-1 peer-focus:text-indigo-600 dark:peer-focus:text-indigo-400">
                Bio (Optional)
              </label>
              <span className="absolute bottom-2 right-2 text-xs text-gray-500">{formData.bio.length}/500</span>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden bg-[#f3f4f6] dark:bg-[#0f172a]">
       {/* Background */}
       <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-50/50 via-white/50 to-purple-50/50 dark:from-indigo-950/30 dark:via-gray-950/80 dark:to-purple-950/30 z-0" />
      </div>

      <div className="w-full max-w-lg relative z-10">
        <div className="mb-8">
          <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
            <span>Start</span>
            <span>Finish</span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / totalSteps) * 100}%` }}
              transition={{ type: "spring", stiffness: 50, damping: 20 }}
            />
          </div>
        </div>

        <GlassCard className="p-8 min-h-[500px] flex flex-col">
          <div className="flex-1 relative">
            <AnimatePresence mode='wait' custom={direction}>
              <motion.div
                key={currentStep}
                custom={direction}
                variants={variants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{ x: { type: "spring", stiffness: 300, damping: 30 }, opacity: { duration: 0.2 } }}
                className="w-full"
              >
                {renderStep()}
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100/10">
            <button 
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`flex items-center gap-2 px-6 py-2 rounded-full font-medium transition-colors ${currentStep === 1 ? 'opacity-0 cursor-default' : 'text-gray-600 dark:text-gray-300 hover:bg-white/10'}`}
            >
              <ChevronLeft size={18} /> Back
            </button>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleNext}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full font-bold shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 transition-shadow"
            >
              {isSubmitting ? 'Creating...' : (currentStep === totalSteps ? 'Finish' : 'Next')} <ChevronRight size={18} />
            </motion.button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default ProfileCreation;