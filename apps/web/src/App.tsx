import Analyze from "./pages/Analyze";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-4">
          <h1 className="text-xl font-bold">GapMate</h1>
          <p className="text-sm text-slate-500">CV ↔ JD match analysis</p>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Analyze />
      </main>
    </div>
  );
}
