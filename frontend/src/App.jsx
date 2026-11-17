import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 flex flex-col">
        {/* Navigation Bar */}
        <header className="bg-slate-900 text-white shadow-md">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center font-black text-xl">
                LG
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight">LPU GoCart</span>
                <span className="block text-[10px] text-blue-400 font-semibold tracking-wider uppercase">
                  Lovely Professional University
                </span>
              </div>
            </div>
            <nav className="flex items-center space-x-6 text-sm font-semibold">
              <Link to="/" className="text-white hover:text-blue-400 transition">Home</Link>
              <Link to="/login" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-xl text-white transition">
                Sign In
              </Link>
            </nav>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">
          <Routes>
            <Route
              path="/"
              element={
                <div className="py-12 text-center space-y-6">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                    Phase 1 Foundation Verified
                  </span>
                  <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight max-w-2xl mx-auto">
                    Smart Campus E-Cart Transit System
                  </h1>
                  <p className="text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
                    Reserve campus e-cart seats, book luggage capacity, track live driver locations, and travel across LPU campus without hassle.
                  </p>
                  <div className="flex justify-center gap-4 pt-4">
                    <Link
                      to="/login"
                      className="px-6 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-600/30 hover:bg-blue-700 transition"
                    >
                      Get Started
                    </Link>
                  </div>
                </div>
              }
            />
            <Route
              path="/login"
              element={
                <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl shadow-xl border border-slate-200 text-center space-y-4">
                  <h2 className="text-2xl font-bold text-slate-900">Sign In to LPU GoCart</h2>
                  <p className="text-sm text-slate-500">Phase 1 Foundation Initialized.</p>
                  <Link to="/" className="inline-block text-blue-600 text-sm font-bold hover:underline">
                    ← Back to Home
                  </Link>
                </div>
              }
            />
          </Routes>
        </main>

        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 font-medium">
          Lovely Professional University, Phagwara, Punjab • LPU GoCart Platform
        </footer>
      </div>
    </BrowserRouter>
  );
}
