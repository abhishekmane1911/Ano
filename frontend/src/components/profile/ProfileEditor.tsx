import { useState, useEffect } from 'react';
import { Loader2, Check } from 'lucide-react';
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
    try {
      const updateData = {
        bio: formData.bio
      };

      const updated = await profileAPI.updateMyProfile(updateData);

      if (avatarFile) {
        const profileWithAvatar = await profileAPI.uploadAvatar(avatarFile);
        setProfile(profileWithAvatar);
      } else {
        setProfile(updated);
      }

      setSuccessMsg('Changes saved');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || !formData) {
    return (
      <div className="min-h-screen w-full bg-slate-50 dark:bg-slate-950 pt-24 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
        <span className="text-sm font-medium text-slate-500">Loading profile...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-slate-50 dark:bg-slate-950 pt-24 pb-12 px-4 sm:px-6 md:px-8 font-sans">
      <div className="w-full max-w-4xl mx-auto">

        {/* Header Section */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white tracking-tight">Profile Settings</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your anonymous identity and bio.</p>
          </div>

          <div className="flex items-center gap-3">
            {successMsg && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-sm font-medium animate-in fade-in slide-in-from-right-4 duration-300">
                <Check className="w-4 h-4" />
                {successMsg}
              </span>
            )}
            <button
              className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-100 dark:text-slate-900 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed tap-target shadow-sm"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column - Avatar */}
          <div className="md:col-span-1">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/50">
                <h2 className="text-sm font-medium text-slate-900 dark:text-white">Avatar</h2>
              </div>
              <div className="p-6 flex justify-center">
                <AnonymousAvatar
                  size="large"
                  currentAvatar={formData.avatar}
                  onImageSelect={(file: File) => setAvatarFile(file)}
                />
              </div>
            </div>
          </div>

          {/* Right Column - Details */}
          <div className="md:col-span-2">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/50">
                <h2 className="text-sm font-medium text-slate-900 dark:text-white">About You</h2>
              </div>

              <div className="p-5 sm:p-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Bio
                  </label>
                  <textarea
                    value={formData.bio || ''}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    rows={5}
                    className="w-full p-3 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 dark:focus:border-blue-500 outline-none transition-all resize-none text-slate-900 dark:text-white text-sm placeholder:text-slate-400"
                    placeholder="Tell others a bit about yourself..."
                    maxLength={500}
                  />
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      Briefly describe yourself.
                    </span>
                    <span className={`text-xs font-medium ${formData.bio?.length >= 490 ? 'text-rose-500' : 'text-slate-400'}`}>
                      {formData.bio?.length || 0}/500
                    </span>
                  </div>
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