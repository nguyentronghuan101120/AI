import React, { useState } from "react";
import OpenAI from "openai";

// Set up OpenAI configuration
const client = new OpenAI({
  apiKey: process.env['OPENAI_API_KEY'], // This is the default and can be omitted
});

function Home() {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);

    try {
      // Make a request to OpenAI's API with streaming
      const stream = await client.chat.completions.create({
        model: "gpt-4o",
        messages: [
          { role: "system", content: "You are a helpful assistant." },
          ...newMessages.map((msg) => ({
            role: msg.sender === "user" ? "user" : "assistant" as "user" | "assistant",
            content: msg.text,
            name: msg.sender === "user" ? "User" : "Assistant",
          })),
        ],
        stream: true,
      });

      let aiMessage = "";
      for await (const chunk of stream) {
        aiMessage += chunk.choices[0]?.delta?.content || '';
        setMessages([...newMessages, { sender: "ai", text: aiMessage }]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages([
        ...newMessages,
        { sender: "ai", text: "Sorry, I couldn't process that. Please try again." },
      ]);
    }

    setInput(""); // Clear input field
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-4 border-b bg-blue-500 text-white text-center text-lg font-semibold">
          AI Chatbot
        </div>
        <div className="p-4 space-y-4 h-96 overflow-y-auto">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-3 rounded-lg ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <div className="flex items-center p-4 border-t">
          <input
            type="text"
            className="flex-grow p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            className="ml-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            onClick={handleSend}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
