export interface Project {
  id: string
  name: string
  description: string | null
  status: string
  meta_data: Record<string, unknown>
  created_at: string
  updated_at: string
}
