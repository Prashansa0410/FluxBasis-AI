export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4 text-gray-900">Welcome to FluxBasis AI</h1>
        <p className="text-xl text-gray-600 mb-8">
          Predictive analytics and model insights platform
        </p>
        <button className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition">
          Get Started
        </button>
      </div>
    </main>
  )
}
