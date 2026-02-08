import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { useLanguage } from '../LanguageContext';

const AICoachChat = ({ taskId, result }) => {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Prepare history for API (exclude current message which is sent separately or included)
      // Our backend API expects history + message
      const history = messages.map(m => ({ role: m.role, content: m.content }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: taskId,
          message: userMessage.content,
          history: history
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const botMessage = { role: 'model', content: data.reply };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'model', content: t('chat_error') }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          style={styles.floatingButton}
        >
          💬 {t('chat_title')}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div style={styles.chatWindow}>
          <div style={styles.chatHeader}>
            <span>🤖 {t('chat_title')}</span>
            <button onClick={() => setIsOpen(false)} style={styles.closeButton}>×</button>
          </div>
          
          <div style={styles.messagesContainer}>
            {messages.length === 0 && (
                <div style={styles.welcomeMessage}>
                    {t('app_subtitle')}
                </div>
            )}
            {messages.map((msg, index) => (
              <div 
                key={index} 
                style={{
                  ...styles.messageBubble,
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  backgroundColor: msg.role === 'user' ? '#1976d2' : '#f1f1f1',
                  color: msg.role === 'user' ? 'white' : 'black',
                }}
              >
                {msg.role === 'user' ? (
                  msg.content
                ) : (
                  <div style={styles.markdownContent}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                )}
              </div>
            ))}
            {loading && <div style={styles.loading}>{t('chat_waiting')}</div>}
            <div ref={messagesEndRef} />
          </div>

          <div style={styles.inputArea}>
            <input
              style={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chat_placeholder')}
              disabled={loading}
            />
            <button 
              onClick={handleSend} 
              style={styles.sendButton}
              disabled={loading}
            >
              {t('send_button')}
            </button>
          </div>
        </div>
      )}
    </>
  );
};

const styles = {
  floatingButton: {
    position: 'fixed',
    bottom: '30px',
    right: '30px',
    padding: '15px 25px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '30px',
    fontSize: '16px',
    cursor: 'pointer',
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
    zIndex: 1000,
  },
  chatWindow: {
    position: 'fixed',
    bottom: '30px',
    right: '30px',
    width: '350px',
    height: '500px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    zIndex: 1000,
    border: '1px solid #ddd'
  },
  chatHeader: {
    padding: '15px',
    backgroundColor: '#1976d2',
    color: 'white',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontWeight: 'bold'
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '20px',
    cursor: 'pointer'
  },
  messagesContainer: {
    flex: 1,
    padding: '15px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    backgroundColor: '#fafafa'
  },
  messageBubble: {
    maxWidth: '80%',
    padding: '10px 15px',
    borderRadius: '18px',
    fontSize: '14px',
    lineHeight: '1.4',
    wordWrap: 'break-word'
  },
  markdownContent: {
    '& p': { margin: '0 0 8px 0' },
    '& ul': { paddingLeft: '20px', margin: '0 0 8px 0' },
    '& li': { marginBottom: '4px' }
  },
  welcomeMessage: {
      textAlign: 'center',
      color: '#888',
      fontSize: '0.9em',
      marginTop: '20px'
  },
  loading: {
    alignSelf: 'flex-start',
    color: '#888',
    fontSize: '12px',
    marginLeft: '10px'
  },
  inputArea: {
    padding: '15px',
    borderTop: '1px solid #eee',
    display: 'flex',
    gap: '10px',
    backgroundColor: 'white'
  },
  input: {
    flex: 1,
    padding: '10px',
    borderRadius: '20px',
    border: '1px solid #ddd',
    outline: 'none',
    fontSize: '14px'
  },
  sendButton: {
    padding: '8px 16px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '14px'
  }
};

export default AICoachChat;
