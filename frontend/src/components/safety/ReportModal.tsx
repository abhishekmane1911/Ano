import { useState } from 'react';
import { createPortal } from 'react-dom'; // IMPORT THIS
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, Ban, HelpCircle, CheckCircle2, MessageSquare, Flag } from 'lucide-react';
import { reportsAPI } from '../../api/reports';
import type { CreateReportData } from '../../api/reports';

interface ReportModalProps {
  reportedUserId: string;
  reportedUserName?: string;
  onClose: () => void;
  onSuccess?: () => void;
}

const ReportModal: React.FC<ReportModalProps> = ({
  reportedUserId,
  reportedUserName = 'Anonymous User',
  onClose,
  onSuccess,
}) => {
  const [reason, setReason] = useState<CreateReportData['reason']>('harassment');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const reasonOptions = [
    { 
      value: 'harassment', 
      label: 'Harassment or Bullying', 
      description: 'Threatening, intimidating, or abusive behavior.',
      icon: AlertTriangle
    },
    { 
      value: 'spam', 
      label: 'Spam', 
      description: 'Repetitive, irrelevant, or promotional content.',
      icon: MessageSquare
    },
    { 
      value: 'inappropriate', 
      label: 'Inappropriate Content', 
      description: 'Sexual, violent, or illegal material.',
      icon: Ban
    },
    { 
      value: 'other', 
      label: 'Other', 
      description: 'Other violations of community guidelines.',
      icon: HelpCircle
    },
  ] as const;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Please provide a description.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await reportsAPI.createReport({
        reported_id: reportedUserId,
        reason,
        description: description.trim(),
      });

      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 2000);
    } catch (err: any) {
      console.error('Failed to submit report:', err);
      setError(err.response?.data?.error || 'Failed to submit report.');
    } finally {
      setLoading(false);
    }
  };

  // Define the modal content JSX
  const modalContent = (
    <AnimatePresence>
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={loading ? undefined : onClose}
        />

        {/* Modal Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="relative w-full max-w-lg bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800 flex flex-col max-h-[90vh]"
          onClick={(e) => e.stopPropagation()}
        >
          {success ? (
            <div className="flex flex-col items-center justify-center p-12 text-center h-full min-h-[400px]">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mb-6">
                <CheckCircle2 size={32} />
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Report Submitted
              </h2>
              <p className="text-gray-500 dark:text-gray-400 text-sm max-w-xs mx-auto">
                Thank you for keeping our community safe. Our team will review this shortly.
              </p>
            </div>
          ) : (
            <>
              {/* Fixed Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm rounded-t-xl z-10">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <Flag className="w-5 h-5 text-red-600 dark:text-red-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white leading-tight">
                      Report User
                    </h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Reporting ID: <span className="font-mono">{reportedUserName}</span>
                    </p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  disabled={loading}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Scrollable Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-700">
                <form id="report-form" onSubmit={handleSubmit} className="space-y-6">
                  
                  <div className="flex gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700/50">
                    <div className="flex-shrink-0 mt-0.5">
                      <HelpCircle className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                      Reports are anonymous. We will review the conversation logs and take appropriate action if a violation is found.
                    </p>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-semibold text-gray-900 dark:text-white block">
                      Reason for report
                    </label>
                    <div className="grid gap-3">
                      {reasonOptions.map((option) => {
                        const Icon = option.icon;
                        const isSelected = reason === option.value;
                        return (
                          <div
                            key={option.value}
                            onClick={() => setReason(option.value as any)}
                            className={`group relative flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                              isSelected
                                ? 'border-red-500 dark:border-red-500 bg-red-50 dark:bg-red-900/10'
                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800/30'
                            }`}
                          >
                            <div className={`mt-0.5 p-1.5 rounded-md ${
                              isSelected ? 'text-red-600 dark:text-red-400' : 'text-gray-400 group-hover:text-gray-600 dark:text-gray-500'
                            }`}>
                              <Icon size={18} />
                            </div>
                            <div>
                              <p className={`text-sm font-medium ${
                                isSelected ? 'text-red-900 dark:text-red-100' : 'text-gray-900 dark:text-gray-200'
                              }`}>
                                {option.label}
                              </p>
                              <p className={`text-xs mt-0.5 ${
                                isSelected ? 'text-red-700 dark:text-red-300' : 'text-gray-500 dark:text-gray-400'
                              }`}>
                                {option.description}
                              </p>
                            </div>
                            <div className={`absolute top-3 right-3 w-4 h-4 rounded-full border flex items-center justify-center ${
                                isSelected ? 'border-red-500 bg-red-500' : 'border-gray-300 dark:border-gray-600'
                            }`}>
                                {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="description" className="text-sm font-semibold text-gray-900 dark:text-white block">
                      Additional details <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Please provide context about what happened..."
                        rows={4}
                        maxLength={500}
                        className="w-full p-3 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-red-500/20 focus:border-red-500 outline-none transition-all resize-none text-gray-900 dark:text-white placeholder:text-gray-400"
                        disabled={loading}
                      />
                      <span className="absolute bottom-2 right-2 text-xs text-gray-400 bg-white dark:bg-gray-800 px-1">
                        {description.length}/500
                      </span>
                    </div>
                  </div>

                  {error && (
                    <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-100 dark:border-red-800">
                      <AlertTriangle size={16} />
                      {error}
                    </div>
                  )}
                </form>
              </div>

              {/* Fixed Footer */}
              <div className="p-6 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 rounded-b-xl">
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={onClose}
                    disabled={loading}
                    className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    form="report-form"
                    disabled={loading || !description.trim()}
                    className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      'Submit Report'
                    )}
                  </button>
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );

  // Use createPortal to render the modal at the document body level
  return createPortal(modalContent, document.body);
};

export default ReportModal;