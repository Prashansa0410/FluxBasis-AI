import type { Config } from 'tailwindcss'
const config: Config = { content: ['./frontend/**/*.{ts,tsx}'], theme: { extend: { colors: { accent: '#2563eb', ink: '#111827' }, boxShadow: { soft: '0 18px 60px rgba(15,23,42,.08)' } } }, plugins: [] }
export default config
