import React, { useState, useEffect } from 'react'
import { supabase } from '../services/supabase'
import StatusItem from './StatusItem'

function StatusList() {
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUploads()
    
    // Subscribe to real-time updates
    const subscription = supabase
      .channel('uploads')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'uploads' },
        (payload) => {
          fetchUploads()
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const fetchUploads = async () => {
    try {
      const { data: session } = await supabase.auth.getSession()
      if (!session?.session?.user) return

      const { data, error } = await supabase
        .from('uploads')
        .select('*')
        .eq('user_id', session.session.user.id)
        .order('uploaded_at', { ascending: false })

      if (error) throw error
      setUploads(data || [])
    } catch (error) {
      console.error('Error fetching uploads:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading uploads...</div>
  }

  return (
    <div className="status-list">
      <h2>Processing Status</h2>
      
      {uploads.length === 0 ? (
        <p className="no-uploads">No uploads yet. Upload a file to get started!</p>
      ) : (
        <div className="uploads-grid">
          {uploads.map((upload) => (
            <StatusItem key={upload.id} upload={upload} />
          ))}
        </div>
      )}
    </div>
  )
}

export default StatusList