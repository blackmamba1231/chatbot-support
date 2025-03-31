"use client";

import React from 'react';
import { ChatContainer } from '../components/chat';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-white">
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-xl font-bold">Vogo.Family</h1>
          <p className="text-sm text-blue-100">Professional Auto Service Support</p>
        </div>
      </header>
      
      <div className="flex-1 container mx-auto p-4 flex flex-col">
        <div className="max-w-4xl mx-auto text-center py-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Welcome to Vogo.Family Auto Services</h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            We provide top-quality auto services for all your vehicle needs. 
            Our team of experts is ready to help you with any car-related issues.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-blue-600 mb-2">Maintenance</h3>
              <p className="text-gray-600">Regular maintenance services to keep your vehicle running smoothly.</p>
            </div>
            
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-blue-600 mb-2">Repairs</h3>
              <p className="text-gray-600">Professional repair services for all makes and models.</p>
            </div>
            
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-blue-600 mb-2">Diagnostics</h3>
              <p className="text-gray-600">Advanced diagnostic tools to identify any issues with your vehicle.</p>
            </div>
          </div>
        </div>
      </div>
      
      <footer className="bg-gray-800 text-white text-center p-4 text-sm">
        <p> 2025 Vogo.Family - All rights reserved</p>
      </footer>
      
      {/* Chat Container */}
      <ChatContainer />
    </main>
  );
}
