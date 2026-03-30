import React, { useState } from 'react';
import { useAPIKeys, apiKeyAPI, formatDateTime } from '../services/backendAPI';

export default function APIKeysPageNew() {
  const { data: apiKeys, loading, error, refetch } = useAPIKeys(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [copiedKeyId, setCopiedKeyId] = useState(null);

  const handleCreateKey = async (e) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);

    try {
      if (!newKeyName.trim()) {
        throw new Error('Key name is required');
      }

      const result = await apiKeyAPI.create(newKeyName);
      setCreatedKey(result);
      setShowKeyModal(true);
      setShowCreateModal(false);
      setNewKeyName('');
      refetch();
      setSuccessMessage('API key created successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.message || 'Failed to create API key');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to revoke this API key? Applications using it will stop working.')) {
      return;
    }

    try {
      setSubmitting(true);
      await apiKeyAPI.delete(keyId);
      setSuccessMessage('API key revoked successfully!');
      refetch();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setFormError(err.message || 'Failed to delete API key');
    } finally {
      setSubmitting(false);
    }
  };

  const copyToClipboard = (text, keyId) => {
    navigator.clipboard.writeText(text);
    setCopiedKeyId(keyId);
    setTimeout(() => setCopiedKeyId(null), 2000);
  };

  const maskKey = (key) => {
    if (!key) return '•••••••••••••';
    return key.substring(0, 4) + '•'.repeat(Math.max(8, key.length - 8)) + key.substring(key.length - 4);
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">API Keys</h1>
          <p className="text-slate-600 mt-1">Manage your API keys for application integrations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-[#006c50] hover:bg-[#004d38] text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
        >
          <span className="material-symbols-outlined">add</span>
          New API Key
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
          <p className="font-semibold">Error loading API keys</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Security Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <span className="material-symbols-outlined text-blue-600 flex-shrink-0">info</span>
        <div className="text-sm text-blue-900">
          <p className="font-semibold mb-1">Keep Your Keys Safe</p>
          <p>Never share your API keys. Treat them like passwords. If compromised, revoke them immediately.</p>
        </div>
      </div>

      {/* API Keys Table */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-slate-200 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : apiKeys?.length === 0 ? (
        <div className="text-center py-16 bg-slate-50 rounded-xl border border-slate-200">
          <div className="material-symbols-outlined text-7xl text-slate-300 mx-auto mb-4">vpn_key</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">No API Keys Yet</h2>
          <p className="text-slate-600 mb-6">Create your first API key to start using the platform</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-[#006c50] hover:bg-[#004d38] text-white px-6 py-2 rounded-lg font-semibold inline-flex items-center gap-2"
          >
            <span className="material-symbols-outlined">add</span>
            Create First API Key
          </button>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {/* Desktop Table */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Key Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Key</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Created</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Status</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {apiKeys.map((key, idx) => (
                  <tr key={key.id || idx} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-slate-900">{key.name}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <code className="bg-slate-100 px-3 py-1 rounded text-xs text-slate-600 font-mono">
                          {key.key_prefix || 'sk-'}•••••
                        </code>
                        <button
                          onClick={() => copyToClipboard(key.full_key || key.key_prefix, key.id)}
                          className="text-slate-400 hover:text-slate-600 p-1"
                          title="Copy key"
                        >
                          <span className="material-symbols-outlined text-base">
                            {copiedKeyId === key.id ? 'check' : 'content_copy'}
                          </span>
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">{formatDateTime(key.created_at)}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          key.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {key.is_active ? 'Active' : 'Revoked'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDeleteKey(key.id)}
                        disabled={submitting || !key.is_active}
                        className="text-red-600 hover:text-red-900 font-semibold flex items-center gap-1 ml-auto disabled:opacity-50"
                      >
                        <span className="material-symbols-outlined text-base">delete</span>
                        Revoke
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Cards */}
          <div className="md:hidden divide-y divide-slate-200">
            {apiKeys.map((key, idx) => (
              <div key={key.id || idx} className="p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900">{key.name}</p>
                    <p className="text-xs text-slate-500 mt-1">{formatDateTime(key.created_at)}</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      key.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {key.is_active ? 'Active' : 'Revoked'}
                  </span>
                </div>
                <div className="flex items-center gap-2 bg-slate-50 p-2 rounded">
                  <code className="flex-1 text-xs font-mono text-slate-600">{maskKey(key.key_prefix)}</code>
                  <button
                    onClick={() => copyToClipboard(key.full_key || key.key_prefix, key.id)}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <span className="material-symbols-outlined text-base">
                      {copiedKeyId === key.id ? 'check' : 'content_copy'}
                    </span>
                  </button>
                </div>
                <button
                  onClick={() => handleDeleteKey(key.id)}
                  disabled={submitting || !key.is_active}
                  className="w-full text-red-600 hover:text-red-900 font-semibold py-2 disabled:opacity-50"
                >
                  Revoke Key
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl">
            {/* Modal Header */}
            <div className="border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900">Create New API Key</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setFormError(null);
                  setNewKeyName('');
                }}
                className="text-slate-400 hover:text-slate-600"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleCreateKey} className="p-6 space-y-4">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-800 text-sm px-3 py-2 rounded">
                  {formError}
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">Key Name *</label>
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production, Staging, Testing"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-[#006c50] focus:ring-2 focus:ring-[#006c50]/20"
                  required
                />
                <p className="text-xs text-slate-500 mt-1">Give your key a descriptive name for easy management</p>
              </div>

              <p className="text-xs text-slate-600 bg-amber-50 border border-amber-200 p-3 rounded">
                <span className="font-semibold">Important:</span> You'll only see the full key once after creation. Save it securely!
              </p>

              <div className="flex gap-3 pt-4 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setFormError(null);
                    setNewKeyName('');
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
                  <span className="material-symbols-outlined">add</span>
                  {submitting ? 'Creating...' : 'Create Key'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Show Generated Key Modal */}
      {showKeyModal && createdKey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl">
            {/* Modal Header */}
            <div className="border-b border-slate-200 px-6 py-4">
              <h2 className="text-xl font-bold text-slate-900">Your API Key</h2>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <div className="bg-green-50 border border-green-200 text-green-800 p-3 rounded-lg flex items-start gap-2">
                <span className="material-symbols-outlined flex-shrink-0 mt-0.5">check_circle</span>
                <div className="text-sm">
                  <p className="font-semibold">Key Created Successfully!</p>
                  <p className="mt-1">Copy and save your API key below. You won't be able to see it again.</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">API Key</label>
                <div className="bg-slate-900 p-4 rounded-lg font-mono text-sm text-green-400 break-all">
                  {createdKey.full_key}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(createdKey.full_key, 'full')}
                  className="flex-1 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-900 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined">content_copy</span>
                  Copy
                </button>
                <button
                  onClick={() => {
                    setShowKeyModal(false);
                    setCreatedKey(null);
                  }}
                  className="flex-1 px-4 py-2 bg-[#006c50] hover:bg-[#004d38] text-white rounded-lg font-semibold transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
