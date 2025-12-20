'use client'

import { useEffect, useState } from 'react'
import { supabase, Tender } from '@/lib/supabase'
import { BarChart, Activity, ShoppingCart, TrendingUp, Anchor, FileText } from 'lucide-react'
import { format } from 'date-fns'

export default function Dashboard() {
  const [tenders, setTenders] = useState<Tender[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTenders()
  }, [])

  const fetchTenders = async () => {
    try {
      const { data, error } = await supabase
        .from('tenders')
        .select('*')
        .order('bid_clse_dt', { ascending: false })
        .limit(10)

      if (error) throw error
      setTenders(data || [])
    } catch (error) {
      console.error('Error fetching tenders:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-8 space-y-8">
      {/* Header */}
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            CarbonFlow Intelligence
          </h1>
          <p className="text-muted mt-1">Real-time Energy Trading Dashboard</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full glass text-sm">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            System Operational
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Active Tenders" value={loading ? "..." : tenders.length.toString()} icon={<FileText className="text-blue-400" />} />
        <StatCard title="Avg. GCV" value="5,820" unit="kcal/kg" icon={<Activity className="text-emerald-400" />} />
        <StatCard title="Bituminous Idx" value="$124.50" change="+2.4%" icon={<TrendingUp className="text-indigo-400" />} />
        <StatCard title="Shipments" value="3" unit="En Route" icon={<Anchor className="text-cyan-400" />} />
      </div>

      {/* Main Content Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Tenders List */}
        <div className="lg:col-span-2 glass rounded-2xl p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-primary" />
            Recent Tenders
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-muted border-b border-border">
                <tr>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Notice No.</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Organization</th>
                  <th className="py-3 px-4">Close Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {loading ? (
                  <tr><td colSpan={5} className="py-8 text-center text-muted">Loading data...</td></tr>
                ) : tenders.length === 0 ? (
                  <tr><td colSpan={5} className="py-8 text-center text-muted">No tenders found</td></tr>
                ) : (
                  tenders.map((tender) => (
                    <tr key={tender.id} className="hover:bg-accent/50 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${tender.status === 'OPEN' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'
                          }`}>
                          {tender.status || 'OPEN'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-muted">{tender.bid_ntce_no}</td>
                      <td className="py-3 px-4 font-medium">{tender.bid_ntce_nm}</td>
                      <td className="py-3 px-4 text-muted">{tender.dminstt_nm}</td>
                      <td className="py-3 px-4 text-muted">
                        {tender.bid_clse_dt ? format(new Date(tender.bid_clse_dt), 'MMM d, HH:mm') : '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Side Panel (Simulations / Market) */}
        <div className="space-y-6">
          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4 text-muted">Market Snapshot</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 rounded-lg bg-card">
                <span>Newcastle (NEWC)</span>
                <span className="font-mono text-emerald-400">$132.00</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-card">
                <span>Indonesia (ICI4)</span>
                <span className="font-mono text-emerald-400">$54.20</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-card">
                <span>Richards Bay (RB)</span>
                <span className="font-mono text-red-400">$110.50</span>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6 h-64 flex flex-col justify-center items-center text-center">
            <BarChart className="w-12 h-12 text-muted mb-4 opacity-50" />
            <p className="text-muted">Netback Simulation Chart</p>
            <p className="text-xs text-gray-500 mt-2">(Coming soon)</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, unit, change, icon }: any) {
  return (
    <div className="glass p-5 rounded-xl hover:bg-accent/50 transition-colors cursor-pointer">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 rounded-lg bg-card">{icon}</div>
        {change && (
          <span className={`text-xs font-medium ${change.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
            {change}
          </span>
        )}
      </div>
      <h3 className="text-muted text-sm font-medium mb-1">{title}</h3>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-foreground">{value}</span>
        {unit && <span className="text-xs text-muted">{unit}</span>}
      </div>
    </div>
  )
}
