'use client';

import { useState } from 'react';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { MallDeliverySearch } from '@/components/mall/MallDeliverySearch';

export default function Home() {
  const [minimized, setMinimized] = useState(false);
  const [showOrderingInterface, setShowOrderingInterface] = useState(false);

  // Function to handle chat messages that request ordering
  const handleChatAction = (action: string) => {
    if (action === 'order_pizza' || action === 'show_products') {
      setShowOrderingInterface(true);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto py-12 px-4">
        <h1 className="text-3xl font-bold text-center text-blue-600 mb-8">
          Vogo.Family Mall Delivery Chatbot
        </h1>
        <p className="text-center text-gray-600 max-w-2xl mx-auto mb-8">
          Welcome to our mall delivery service! Our AI-powered chatbot can help you find products from various shopping malls across Romania, including Alba Iulia, Arad, Miercurea Ciuc, and Vaslui.
        </p>
        
        {/* Button to toggle between chat and ordering interface */}
        <div className="flex justify-center mb-12">
          <button 
            onClick={() => setShowOrderingInterface(!showOrderingInterface)}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            {showOrderingInterface ? 'Return to Chat' : 'Order Now'}
          </button>
        </div>

        {/* Show either the ordering interface or just the chat container */}
        {showOrderingInterface ? (
          <div className="max-w-6xl mx-auto">
            <MallDeliverySearch />
          </div>
        ) : null}
      </div>

      {/* Chat container is always visible */}
      <ChatContainer 
        minimized={minimized} 
        onMinimize={() => setMinimized(!minimized)}
        onAction={handleChatAction}
      />
    </main>
  );
}