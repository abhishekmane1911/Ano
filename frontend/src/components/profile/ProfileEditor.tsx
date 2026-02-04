import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
// Minimized imports - removed decorative icons
import InterestSelector from './InterestSelector';
import AnonymousAvatar from './AnonymousAvatar';
import { profileAPI } from '../../api/profile';
import { useProfileStore } from '../../stores/profileStore';

const ProfileEditor = () => {
  const { profile, setProfile, isLoading, setLoading, setError } = useProfileStore();
  const [formData, setFormData] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (profile) {
      setFormData(profile);
    } else {
      setLoading(true);
      profileAPI.getMyProfile()
        .then(p => {
          setProfile(p);
          setFormData(p);
        })
        .catch((err) => {
          setError(err.message || 'Failed to load profile');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [profile, setProfile, setLoading, setError]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setLoading(true);
    try {
      const updateData = {
        age: formData.age,
        interests: formData.interests,
        hobbies: formData.hobbies,
        relationship_intent: formData.relationship_intent,
        personality_tags: formData.personality_tags,
        bio: formData.bio
      };
      
      const updated = await profileAPI.updateMyProfile(updateData);
      
      if (avatarFile) {
        const profileWithAvatar = await profileAPI.uploadAvatar(avatarFile);
        setProfile(profileWithAvatar);
      } else {
        setProfile(updated);
      }
      
      setSuccessMsg('Changes saved successfully');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  if (isLoading || !formData) {
    return (
      <div className="min-h-screen w-full bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    // ADDED pt-24 to fix top overlap
    <div className="min-h-screen w-full bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 pb-12 px-4 selection:bg-indigo-500/30">
      
       {/* Background */}
       <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-50/50 via-white/50 to-purple-50/50 dark:from-indigo-950/30 dark:via-gray-950/80 dark:to-purple-950/30" />
      </div>

      <div className="relative z-10 w-full max-w-5xl mx-auto">
        {/* Header Section */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 dark:border-gray-800 pb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Manage your anonymous identity</p>
          </div>
          <div className="flex items-center gap-4">
            {successMsg && <span className="text-green-600 dark:text-green-400 text-sm font-medium">{successMsg}</span>}
            <button
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Avatar & Core Info */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <div className="flex flex-col items-center text-center">
                <div className="mb-6">
                  <AnonymousAvatar 
                    size="large" 
                    currentAvatar={formData.avatar}
                    onImageSelect={(file: File) => setAvatarFile(file)} 
                  />
                </div>
                
                <div className="w-full space-y-4 text-left">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Display Age</label>
                    <input 
                      type="number"
                      value={formData.age}
                      onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Intent</label>
                    <div className="space-y-2">
                      {['friendship', 'dating', 'casual'].map(intent => (
                        <label key={intent} className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
                          formData.relationship_intent === intent 
                            ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300' 
                            : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}>
                            <span className="capitalize text-sm font-medium">{intent}</span>
                            <input 
                              type="radio" 
                              name="edit-intent" 
                              value={intent}
                              checked={formData.relationship_intent === intent}
                              onChange={(e) => setFormData({...formData, relationship_intent: e.target.value})}
                              className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                            />
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Details */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">About You</h3>
              
              <div className="space-y-6">
                <InterestSelector 
                  label="Interests"
                  selectedItems={formData.interests}
                  onChange={(items: any) => setFormData({...formData, interests: items})}
                  suggestions={['Music', 'Movies', 'Design', 'Coding']}
                />

                <InterestSelector 
                  label="Hobbies"
                  selectedItems={formData.hobbies}
                  onChange={(items: any) => setFormData({...formData, hobbies: items})}
                  suggestions={['Gaming', 'Photography', 'Reading']}
                />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Personality</h3>

              <div className="space-y-6">
                <InterestSelector 
                  label="Personality Tags"
                  selectedItems={formData.personality_tags}
                  onChange={(items: any) => setFormData({...formData, personality_tags: items})}
                  suggestions={['Creative', 'Logical', 'Chill', 'Energetic']}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bio</label>
                  <textarea
                    value={formData.bio}
                    onChange={(e) => setFormData({...formData, bio: e.target.value})}
                    rows={4}
                    className="w-full p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none text-gray-900 dark:text-white"
                    placeholder="Tell others a bit about yourself..."
                    maxLength={500}
                  />
                  <div className="text-right mt-1 text-xs text-gray-500">{formData.bio?.length || 0}/500</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileEditor;