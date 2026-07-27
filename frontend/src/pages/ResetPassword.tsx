import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Loader2, Check, X } from 'lucide-react'
import { authApi } from '../api/endpoints'

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const passwordsMatch = confirmPassword.length > 0 && newPassword === confirmPassword
  const passwordsMismatch = confirmPassword.length > 0 && newPassword !== confirmPassword

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await authApi.resetPassword(token, newPassword)
      setSuccess(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Something went wrong. The link may have expired.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-sm text-center">
          <p className="text-sm text-red-600">Invalid or missing reset token.</p>
          <a href="/forgot-password" className="mt-4 block text-sm text-blue-600 hover:underline">
            Request a new reset link
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-1">Set a new password</h1>
        <p className="text-sm text-gray-500 mb-6">Enter your new password below.</p>

        {success ? (
          <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-3">
            Password reset successful. Redirecting to login...
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label htmlFor="new-password" className="sr-only">New password</label>
              <input
                id="new-password"
                name="new-password"
                type="password"
                required
                minLength={6}
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="confirm-password" className="sr-only">Confirm new password</label>
              <div className="relative">
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  required
                  minLength={6}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 pr-9 text-sm focus:outline-none focus:ring-2 ${
                    passwordsMismatch
                      ? 'border-red-400 focus:ring-red-400'
                      : passwordsMatch
                      ? 'border-green-400 focus:ring-green-400'
                      : 'border-gray-300 focus:ring-blue-500'
                  }`}
                />
                {passwordsMatch && (
                  <Check size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500" />
                )}
                {passwordsMismatch && (
                  <X size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500" />
                )}
              </div>
              {passwordsMismatch && (
                <p className="text-xs text-red-600 mt-1">Passwords do not match.</p>
              )}
              {passwordsMatch && (
                <p className="text-xs text-green-600 mt-1">Passwords match.</p>
              )}
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              disabled={loading || !passwordsMatch}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              Reset password
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default ResetPassword
