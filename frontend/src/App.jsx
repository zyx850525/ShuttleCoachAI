import { useState, useEffect } from 'react'
import VideoUpload from './components/VideoUpload'
import AnalysisResult from './components/AnalysisResult'
import { LanguageProvider, useLanguage } from './LanguageContext';

function AppContent() {
  const { t, toggleLanguage, language } = useLanguage();
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, failed
  const [analysisStartTime, setAnalysisStartTime] = useState(null);
  const [analysisDuration, setAnalysisDuration] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // URL Persistence Logic
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const taskId = params.get('taskId');
    
    if (taskId) {
      // Restore from URL: Immediately fetch status without showing "Processing" first if possible
      setCurrentTaskId(taskId);
      setStatus('restoring'); // New intermediate state
      
      // Perform an immediate fetch
      fetch(`/api/result/${taskId}`)
        .then(res => {
            if (res.status === 404) {
                setStatus('idle'); // Task not found, reset
                updateUrl(null);
                return null;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.status === 'completed') {
                setAnalysisResult(data);
                setStatus('completed');
            } else if (data.status === 'failed') {
                setStatus('failed');
                alert(`Analysis failed: ${data.error}`);
            } else {
                setStatus('processing'); // Still processing, switch to polling
            }
        })
        .catch(err => {
            console.error("Restoration fetch error", err);
            setStatus('idle');
        });
    }

    // Handle browser back/forward buttons
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const taskId = params.get('taskId');
      if (taskId) {
        setCurrentTaskId(taskId);
        // For back/forward, we might also want to do an immediate check
        setStatus('processing'); 
      } else {
        handleReset();
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Update URL when task ID changes
  const updateUrl = (taskId) => {
    if (taskId) {
      const newUrl = `${window.location.pathname}?taskId=${taskId}`;
      window.history.pushState({ path: newUrl }, '', newUrl);
    } else {
      const newUrl = window.location.pathname;
      window.history.pushState({ path: newUrl }, '', newUrl);
    }
  };

  // Timer for elapsed time
  useEffect(() => {
    let timer;
    if (status === 'processing' && analysisStartTime) {
      timer = setInterval(() => {
        setElapsedTime(((Date.now() - analysisStartTime) / 1000).toFixed(1));
      }, 100);
    }
    return () => clearInterval(timer);
  }, [status, analysisStartTime]);

  // Poll for results when we have a task ID
  useEffect(() => {
    if (!currentTaskId || status === 'completed') return;

    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/result/${currentTaskId}`);
        if (res.status === 404) return; // Not ready yet potentially? Or invalid ID.
        
        const data = await res.json();
        
        if (data.status === 'completed') {
          setAnalysisResult(data);
          setStatus('completed');
          
          if (analysisStartTime) {
            const duration = ((Date.now() - analysisStartTime) / 1000).toFixed(1);
            setAnalysisDuration(duration);
          }
          
          clearInterval(pollInterval);
        } else if (data.status === 'failed') {
          setStatus('failed');
          alert(`Analysis failed: ${data.error}`);
          clearInterval(pollInterval);
        } else {
          setStatus('processing');
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [currentTaskId, status]);

  const handleUploadSuccess = (taskId) => {
    setCurrentTaskId(taskId);
    setStatus('processing');
    setAnalysisResult(null);
    setAnalysisStartTime(Date.now());
    setAnalysisDuration(null);
    setElapsedTime(0);
    updateUrl(taskId);
  };

  const handleReset = () => {
    setCurrentTaskId(null);
    setAnalysisResult(null);
    setStatus('idle');
    setAnalysisStartTime(null);
    setAnalysisDuration(null);
    setElapsedTime(0);
    updateUrl(null);
  };

  return (
    <div className="app-container">
      <header style={styles.header}>
        <div style={styles.langSwitchContainer}>
          <button onClick={toggleLanguage} style={styles.langButton}>
            {language === 'zh' ? 'EN' : '中文'}
          </button>
        </div>
        <h1>🏸 {t('app_title')}</h1>
        <p>{t('app_subtitle')}</p>
      </header>

      <main style={styles.main}>
        {status === 'idle' && (
          <VideoUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {(status === 'processing' || status === 'restoring') && (
          <div style={styles.loading}>
            <div className="spinner"></div>
            {status === 'restoring' ? (
                <h3>{t('analyzing_restore')}</h3>
            ) : (
                <>
                    <h3>{t('analyzing_title')}</h3>
                    <p>{t('elapsed_time')}: {elapsedTime} {t('seconds')}</p>
                    <p>{t('analyzing_wait')}</p>
                </>
            )}
          </div>
        )}

        {status === 'completed' && analysisResult && (
          <div>
            <button onClick={handleReset} style={styles.backButton}>{t('back_button')}</button>
            <AnalysisResult result={analysisResult} duration={analysisDuration} />
          </div>
        )}
      </main>
    </div>
  )
}

const styles = {
  header: {
    backgroundColor: '#1a73e8',
    color: 'white',
    padding: '20px',
    textAlign: 'center',
    position: 'relative'
  },
  langSwitchContainer: {
    position: 'absolute',
    top: '20px',
    right: '20px'
  },
  langButton: {
    padding: '5px 10px',
    fontSize: '14px',
    backgroundColor: 'rgba(255,255,255,0.2)',
    color: 'white',
    border: '1px solid rgba(255,255,255,0.5)',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  main: {
    padding: '20px',
    maxWidth: '1000px',
    margin: '0 auto'
  },
  loading: {
    textAlign: 'center',
    padding: '50px',
    color: '#666'
  },
  backButton: {
    padding: '8px 16px',
    marginBottom: '20px',
    cursor: 'pointer',
    backgroundColor: 'transparent',
    border: '1px solid #ccc',
    borderRadius: '4px'
  }
};

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}

export default App
