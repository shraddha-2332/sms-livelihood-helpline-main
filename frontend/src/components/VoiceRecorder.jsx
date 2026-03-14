import React, { useState, useEffect, useRef } from 'react'
import { 
  Mic, 
  StopCircle, 
  Play, 
  Trash2, 
  Send,
  Phone,
  PhoneCall,
  PhoneIncoming,
  PhoneOutgoing,
  Clock,
  CheckCircle
} from 'lucide-react'
import axios from 'axios'
import API_BASE from '../config/apiBase'

export default function VoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const audioRef = useRef(null)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [voiceCalls, setVoiceCalls] = useState([])
  const [loadingCalls, setLoadingCalls] = useState(true)

  useEffect(() => {
    fetchVoiceCalls()
    // Refresh every 15 seconds
    const interval = setInterval(fetchVoiceCalls, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchVoiceCalls = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/voice/calls`)
      setVoiceCalls(response.data.calls || [])
    } catch (error) {
      console.error('Error fetching voice calls:', error)
    } finally {
      setLoadingCalls(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const preferredTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
      ]
      const mimeType = preferredTypes.find(type => MediaRecorder.isTypeSupported(type)) || ''
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      const chunks = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data)
        }
      }

      recorder.onstop = () => {
        const blobType = recorder.mimeType || 'audio/webm'
        const blob = new Blob(chunks, { type: blobType })
        if (blob.size === 0) {
          alert('Recording failed. Please try again and allow microphone access.')
          return
        }
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(track => track.stop())
      }

      recorder.start(100)
      setMediaRecorder(recorder)
      setIsRecording(true)
      setResult(null)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
    }
  }

  const playRecording = () => {
    if (audioRef.current) {
      audioRef.current
        .play()
        .catch(() => {})
    }
  }

  const deleteRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }
    setAudioBlob(null)
    setAudioUrl(null)
    setResult(null)
  }

  const processVoice = async () => {
    if (!audioBlob || !phoneNumber.trim()) {
      alert('Please provide a phone number and record audio')
      return
    }

    try {
      setProcessing(true)

      // Convert blob to base64
      const reader = new FileReader()
      reader.readAsDataURL(audioBlob)
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1]

        const response = await axios.post(`${API_BASE}/api/voice/process`, {
          phone: phoneNumber,
          audio_base64: base64Audio
        })

        setResult(response.data)
        fetchVoiceCalls()
        
        // Clear form
        deleteRecording()
        setPhoneNumber('')
      }
    } catch (error) {
      console.error('Error processing voice:', error)
      alert('Failed to process voice. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Voice Call Management</h2>
          <p className="text-gray-600">Record and process voice messages</p>
        </div>

        {/* Voice Recorder Card */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Record Voice Message</h3>
          
          {/* Phone Number Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+91 9876543210"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Recording Controls */}
          <div className="flex flex-col items-center justify-center space-y-6 py-8">
            {/* Recording Button */}
            <div className="relative">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={processing}
                className={`w-24 h-24 rounded-full flex items-center justify-center transition-all shadow-lg ${
                  isRecording
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                    : 'bg-blue-600 hover:bg-blue-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isRecording ? (
                  <StopCircle size={40} className="text-white" />
                ) : (
                  <Mic size={40} className="text-white" />
                )}
              </button>
              
              {isRecording && (
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                  <span className="text-sm font-medium text-red-600">Recording...</span>
                </div>
              )}
            </div>

            {/* Recording Info */}
            {!isRecording && !audioBlob && (
              <p className="text-gray-600 text-center">
                Click the microphone to start recording
              </p>
            )}

            {/* Audio Playback Controls */}
            {audioBlob && !isRecording && (
              <div className="w-full max-w-md space-y-4">
                <div className="bg-gray-100 rounded-lg p-4">
                  <div className="flex items-center justify-center gap-4">
                    <button
                      onClick={playRecording}
                      className="p-3 bg-white rounded-full shadow hover:shadow-md transition-shadow"
                    >
                      <Play size={24} className="text-gray-700" />
                    </button>
                    
                    <div className="flex-1 text-center">
                      <p className="text-sm font-medium text-gray-700">Recording ready</p>
                      <p className="text-xs text-gray-500">Click play to listen</p>
                    </div>

                    <button
                      onClick={deleteRecording}
                      className="p-3 bg-white rounded-full shadow hover:shadow-md transition-shadow"
                    >
                      <Trash2 size={24} className="text-red-600" />
                    </button>
                  </div>
                  <div className="mt-4">
                    <audio ref={audioRef} controls src={audioUrl} className="w-full" preload="auto" />
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    {audioBlob ? `File size: ${(audioBlob.size / 1024).toFixed(1)} KB` : ''}
                  </div>
                </div>

                {/* Process Button */}
                <button
                  onClick={processVoice}
                  disabled={processing || !phoneNumber.trim()}
                  className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {processing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Process Voice Message
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Result Display */}
          {result && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
                <CheckCircle size={20} />
                Voice Processed Successfully
              </h4>
              <div className="space-y-2 text-sm text-green-800">
                <p><strong>Transcription:</strong> {result.transcription}</p>
                <p><strong>Duration:</strong> {formatDuration(result.duration)}</p>
                <p><strong>Message ID:</strong> #{result.message_id}</p>
              </div>
            </div>
          )}
        </div>

        {/* Voice Calls History */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Voice Call History</h3>
            <button
              onClick={fetchVoiceCalls}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Refresh
            </button>
          </div>

          {loadingCalls ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : voiceCalls.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <PhoneCall size={48} className="mx-auto mb-4 opacity-50" />
              <p>No voice calls recorded yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">ID</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Phone</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Direction</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Duration</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Transcription</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {voiceCalls.map((call) => (
                    <tr key={call.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">#{call.id}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{call.phone}</td>
                      <td className="px-4 py-3">
                        <span className="flex items-center gap-1 text-sm">
                          {call.direction === 'inbound' ? (
                            <>
                              <PhoneIncoming size={14} className="text-green-600" />
                              <span className="text-green-600">Inbound</span>
                            </>
                          ) : (
                            <>
                              <PhoneOutgoing size={14} className="text-blue-600" />
                              <span className="text-blue-600">Outbound</span>
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {call.duration ? formatDuration(call.duration) : '-'}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          call.status === 'completed' ? 'bg-green-100 text-green-800' :
                          call.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {call.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                        {call.transcription || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {formatTime(call.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="card bg-blue-50 border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">About Voice Processing</h4>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• Voice messages are automatically transcribed to text</li>
            <li>• Transcriptions are processed by the intent classifier</li>
            <li>• Tickets are created automatically from voice messages</li>
            <li>• Support for multiple Indian languages coming soon</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

