'use client';

import dynamic from 'next/dynamic';

// Import your SwiftPredict component with SSR disabled
const SwiftPredictUI = dynamic(() => import('./SwiftPredictUI'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading SwiftPredict...</p>
      </div>
    </div>
  )
});

export default function Page() {
  return <SwiftPredictUI />;
}