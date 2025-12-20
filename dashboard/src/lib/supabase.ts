import { createClient } from '@supabase/supabase-js'

// Environment variables - set in .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ""
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ""

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn("⚠️ Supabase credentials not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Tender = {
    id: string
    bid_ntce_no: string
    bid_ntce_nm: string
    dminstt_nm: string
    bid_clse_dt: string
    status: string
}
