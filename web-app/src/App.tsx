import React from "react";
import Chat from "./components/Chat";

const App: React.FC = () => {
  return (
    <div className="h-screen bg-gray-100">
      <div className="mx-auto max-w-4xl h-full">
        <Chat />
      </div>
    </div>
  );
};

export default App;
