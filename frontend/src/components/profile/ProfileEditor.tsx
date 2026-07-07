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
      <div className="min-h-screen w-full bg-zinc-950 pt-24 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-5 h-5 animate-spin text-zinc-500" />
        <span className="text-sm font-medium text-zinc-400">Loading profile...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-zinc-950 pt-24 pb-12 px-4 sm:px-6 md:px-8 font-sans">
      <div className="w-full max-w-5xl mx-auto space-y-8">

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div className="space-y-1.5">
            <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">Profile Settings</h1>
            <p className="text-sm text-zinc-400">Manage your anonymous identity and personal bio.</p>
          </div>

          <div className="flex items-center gap-3">
            {successMsg && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium animate-in fade-in slide-in-from-right-4 duration-300">
                <Check className="w-4 h-4" />
                {successMsg}
              </span>
            )}
            <button
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-zinc-100 hover:bg-white text-zinc-900 rounded-lg text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-950 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm tap-target"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <div className="lg:col-span-1">
            <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl shadow-sm p-6 flex flex-col items-center justify-center h-full min-h-[300px]">
              <h2 className="text-sm font-medium text-zinc-100 mb-8 self-start w-full">Avatar</h2>
              <AnonymousAvatar
                size="large"
                currentAvatar={formData.avatar}
                onImageSelect={(file: File) => setAvatarFile(file)}
              />
            </div>
          </div>


          <div className="lg:col-span-2">
            <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl shadow-sm p-6 flex flex-col h-full">
              <h2 className="text-sm font-medium text-zinc-100 mb-6">About You</h2>

              <div className="flex-1 flex flex-col">
                <label htmlFor="bio" className="block text-sm font-medium text-zinc-300 mb-2.5">
                  Bio
                </label>
                <textarea
                  id="bio"
                  value={formData.bio || ''}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  rows={6}
                  className="w-full flex-1 p-3.5 bg-zinc-950/50 border border-zinc-800/80 rounded-lg focus:ring-1 focus:ring-zinc-700 focus:border-zinc-700 outline-none transition-all resize-none text-zinc-100 text-sm placeholder:text-zinc-600 shadow-inner"
                  placeholder="Tell others a bit about yourself..."
                  maxLength={500}
                />
                <div className="flex justify-between items-center mt-3">
                  <span className="text-xs text-zinc-500">
                    Briefly describe yourself. This will be visible on your profile.
                  </span>
                  <span className={`text-xs font-medium tabular-nums ${formData.bio?.length >= 490 ? 'text-rose-500' : 'text-zinc-500'}`}>
                    {formData.bio?.length || 0}/500
                  </span>
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