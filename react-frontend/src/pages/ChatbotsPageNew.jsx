import React, { useState } from 'react';
import { useChatbots, chatbotAPI, formatDateTime } from '../services/backendAPI';

export default function ChatbotsPageNew() {
  const { data: chatbots, loading, error, refetch } = useChatbots(true);
  const [showModal, setShowModal] = useState(false);
  const [editingBot, setEditingBot] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    system_prompt: '',
    llm_model: 'gpt-4o-mini',
    temperature: 0.7,
    max_tokens: 1024,
  });

  const resetForm = () => {
    setFormData({
      name: '',
      system_prompt: '',
      llm_model: 'gpt-4o-mini',
      temperature: 0.7,
      max_tokens: 1024,
    });
    setEditingBot(null);
    setFormError(null);
  };

  const openCreateModal = () => {
    resetForm();
    setShowModal(true);
  };

  const openEditModal = (bot) => {
    setFormData({
      name: bot.name || '',
      system_prompt: bot.system_prompt || '',
      llm_model: bot.llm_model || 'gpt-4o-mini',
      temperature: bot.temperature || 0.7,
      max_tokens: bot.max_tokens || 1024,
    });
    setEditingBot(bot);
    setShowModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name.includes('temperature') || name.includes('max_tokens') ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);

    try {
      if (!formData.name.trim()) {
        throw new Error('Chatbot name is required');
      }

      if (editingBot) {
        // Update existing chatbot
        await chatbotAPI.update(editingBot.id, formData);
        setSuccessMessage('Chatbot updated successfully!');
      } else {
        // Create new chatbot
        await chatbotAPI.create(formData);
        setSuccessMessage('Chatbot created successfully!');
      }

      setShowModal(false);
      resetForm();
      refetch();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.message || 'Failed to save chatbot');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (botId) => {
    if (!window.confirm('Are you sure you want to delete this chatbot? This action cannot be undone.')) {
      return;
    }

    try {
      setSubmitting(true);
      await chatbotAPI.delete(botId);
      setSuccessMessage('Chatbot deleted successfully!');
      refetch();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.message || 'Failed to delete chatbot');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Chatbots</h1>
          <p className="text-slate-600 mt-1">Manage all your AI chatbot instances</p>
        </div>
        <button
          onClick={openCreateModal}
          className="bg-[#006c50] hover:bg-[#004d38] text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
        >
          <span className="material-symbols-outlined">add</span>
          Create Chatbot
        </button>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2">
          <span className="material-symbols-outlined text-green-600">check_circle</span>
          {successMessage}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          <p className="font-semibold">Error loading chatbots</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Chatbots Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-64 bg-slate-200 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : chatbots?.length === 0 ? (
        <div className="text-center py-16 bg-slate-50 rounded-xl border border-slate-200">
          <div className="material-symbols-outlined text-7xl text-slate-300 mx-auto mb-4">smart_toy</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">No Chatbots Yet</h2>
          <p className="text-slate-600 mb-6">Create your first AI chatbot to get started</p>
          <button
            onClick={openCreateModal}
            className="bg-[#006c50] hover:bg-[#004d38] text-white px-6 py-2 rounded-lg font-semibold inline-flex items-center gap-2"
          >
            <span className="material-symbols-outlined">add</span>
            Create First Chatbot
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {chatbots.map((bot, idx) => (
            <div
              key={bot.id || idx}
              className="bg-white border border-slate-200 rounded-xl p-6 hover:border-[#006c50] transition-all duration-300 group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-[#006c50]/10 text-[#006c50] p-3 rounded-lg">
                    <span className="material-symbols-outlined">smart_toy</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-slate-900 truncate text-lg">{bot.name}</h3>
                    <span
                      className={`inline-block text-xs font-semibold px-2 py-1 rounded mt-1 ${
                        bot.status?.toLowerCase() === 'active' || bot.status === 'ACTIVE'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {bot.status || 'Active'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2 mb-4 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>Model:</span>
                  <span className="font-medium text-slate-900">{bot.llm_model || 'gpt-4o-mini'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Temperature:</span>
                  <span className="font-medium text-slate-900">{bot.temperature || 0.7}</span>
                </div>
                <div className="flex justify-between">
                  <span>Max Tokens:</span>
                  <span className="font-medium text-slate-900">{bot.max_tokens || 1024}</span>
                </div>
              </div>

              {/* Timestamp */}
              {bot.created_at && (
                <p className="text-xs text-slate-400 mb-4">Created: {formatDateTime(bot.created_at)}</p>
              )}

              {/* Prompt Preview */}
              {bot.system_prompt && (
                <div className="bg-slate-50 rounded p-2 mb-4">
                  <p className="text-xs text-slate-600 line-clamp-2">{bot.system_prompt}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => openEditModal(bot)}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg font-semibold text-sm transition-colors flex items-center justify-center gap-1"
                >
                  <span className="material-symbols-outlined text-base">edit</span>
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(bot.id)}
                  disabled={submitting}
                  className="flex-1 px-3 py-2 bg-red-50 text-red-700 hover:bg-red-100 rounded-lg font-semibold text-sm transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-base">delete</span>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full max-h-96 overflow-y-auto shadow-xl">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900">
                {editingBot ? 'Edit Chatbot' : 'Create New Chatbot'}
              </h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  resetForm();
                }}
                className="text-slate-400 hover:text-slate-600"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-800 text-sm px-3 py-2 rounded">
                  {formError}
                </div>
              )}

              {/* Chatbot Name */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">Chatbot Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Customer Support Bot"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-[#006c50] focus:ring-2 focus:ring-[#006c50]/20"
                  required
                />
              </div>

              {/* System Prompt */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">System Prompt</label>
                <textarea
                  name="system_prompt"
                  value={formData.system_prompt}
                  onChange={handleInputChange}
                  placeholder="Define how the chatbot should behave..."
                  rows="3"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-[#006c50] focus:ring-2 focus:ring-[#006c50]/20 resize-none"
                />
              </div>

              {/* LLM Model */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">Model</label>
                <select
                  name="llm_model"
                  value={formData.llm_model}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-[#006c50] focus:ring-2 focus:ring-[#006c50]/20"
                >
                  <option value="gpt-4o-mini">GPT-4 Mini (Fast & Affordable)</option>
                  <option value="gpt-4">GPT-4 (Advanced)</option>
                  <option value="groq/llama-3.3-70b-versatile">Llama 3.3 70B (Open Source)</option>
                </select>
              </div>

              {/* Temperature */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Temperature: {formData.temperature}
                </label>
                <input
                  type="range"
                  name="temperature"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={handleInputChange}
                  className="w-full"
                />
                <p className="text-xs text-slate-500 mt-1">Lower = more focused, Higher = more creative</p>
              </div>

              {/* Max Tokens */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">Max Tokens</label>
                <input
                  type="number"
                  name="max_tokens"
                  value={formData.max_tokens}
                  onChange={handleInputChange}
                  min="100"
                  max="4096"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-[#006c50] focus:ring-2 focus:ring-[#006c50]/20"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 text-slate-700 border border-slate-300 rounded-lg font-semibold hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-[#006c50] hover:bg-[#004d38] text-white rounded-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined">{editingBot ? 'save' : 'add'}</span>
                  {submitting ? 'Saving...' : editingBot ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
